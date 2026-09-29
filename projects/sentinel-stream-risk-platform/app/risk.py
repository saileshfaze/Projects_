from dataclasses import dataclass
import numpy as np
from sklearn.ensemble import IsolationForest
from .schemas import Transaction,RiskDecision

@dataclass
class RiskEngine:
    threshold: float=0.68
    seed: int=42
    def __post_init__(self)->None:
        rng=np.random.default_rng(self.seed)
        normal=np.column_stack([rng.lognormal(3.6,.7,800),rng.poisson(3,800),rng.normal(1,.35,800).clip(.05,5),rng.integers(30,2500,800)])
        self.model=IsolationForest(n_estimators=120,contamination=.04,random_state=self.seed).fit(normal)
    def score(self,tx:Transaction)->RiskDecision:
        ratio=tx.amount_eur/max(tx.avg_amount_30d,1)
        x=np.array([[tx.amount_eur,tx.tx_count_24h,ratio,tx.account_age_days]])
        anomaly=float(-self.model.score_samples(x)[0]); anomaly_norm=float(np.clip((anomaly-.35)/.45,0,1))
        reasons=[]; rule=0.0
        if ratio>=5: rule+=.30; reasons.append("amount_5x_customer_baseline")
        if tx.tx_count_24h>=15: rule+=.25; reasons.append("high_24h_velocity")
        if tx.account_age_days<14 and tx.amount_eur>1000: rule+=.20; reasons.append("young_account_high_value")
        if tx.channel=="ecommerce" and tx.amount_eur>2500: rule+=.10; reasons.append("high_value_ecommerce")
        score=float(np.clip(.55*anomaly_norm+rule,0,1))
        if anomaly_norm>.70: reasons.append("ml_behavioral_anomaly")
        decision="block" if score>=self.threshold+.18 else "review" if score>=self.threshold else "allow"
        return RiskDecision(transaction_id=tx.transaction_id,score=round(score,4),decision=decision,reasons=reasons or ["within_expected_behavior"],model_version="hybrid-iforest-0.1")
