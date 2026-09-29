import os
os.environ["DATABASE_URL"]="sqlite:///:memory:"
from fastapi.testclient import TestClient
from app.main import app
client=TestClient(app)
def test_health():
    r=client.get("/health"); assert r.status_code==200; assert r.json()["status"]=="ok"
def test_score_contract():
    p={"transaction_id":"tx-api-001","account_id":"acct-api","amount_eur":75,"merchant_category":"travel","country":"IT","channel":"wallet","account_age_days":700,"tx_count_24h":2,"avg_amount_30d":80}
    r=client.post("/v1/score",json=p); assert r.status_code==200
    assert set(r.json())=={"transaction_id","score","decision","reasons","model_version"}
