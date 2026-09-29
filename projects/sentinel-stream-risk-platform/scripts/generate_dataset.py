from pathlib import Path
import csv,random
random.seed(42)
out=Path("data/generated/transactions.csv"); out.parent.mkdir(parents=True,exist_ok=True)
countries=["IT","DE","FR","ES","NL"]; channels=["card_present","ecommerce","transfer","wallet"]
with out.open("w",newline="") as f:
    w=csv.writer(f); w.writerow(["transaction_id","account_id","amount_eur","country","channel","is_fraud"])
    for i in range(1500):
        anomaly=random.random()<.045; amount=round(random.lognormvariate(3.7 if not anomaly else 7.0,.7),2)
        w.writerow([f"tx-{i:06}",f"acct-{random.randint(1,300):04}",amount,random.choice(countries),random.choice(channels),int(anomaly)])
print(f"generated {out}")
