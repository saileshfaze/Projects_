from app.risk import RiskEngine
from app.schemas import Transaction

def tx(**overrides):
    base=dict(transaction_id="tx-test-001",account_id="acct-1",amount_eur=50,merchant_category="grocery",country="IT",channel="card_present",account_age_days=500,tx_count_24h=2,avg_amount_30d=55)
    base.update(overrides); return Transaction(**base)
def test_normal_payment_is_allowed():
    result=RiskEngine().score(tx()); assert result.decision=="allow"; assert 0<=result.score<=1
def test_extreme_velocity_has_reason_code():
    result=RiskEngine().score(tx(amount_eur=6000,avg_amount_30d=100,tx_count_24h=25))
    assert "amount_5x_customer_baseline" in result.reasons
    assert "high_24h_velocity" in result.reasons
    assert result.decision in {"review","block"}
