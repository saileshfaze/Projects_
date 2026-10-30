"""Local FastAPI smoke check without opening a network port."""
from fastapi.testclient import TestClient
from skyweave.api import app
from skyweave.scenarios import crossing
from skyweave.models import flights_payload

client=TestClient(app)
assert client.get('/health').status_code==200
r=client.post('/v1/analyze',json=flights_payload(crossing()))
assert r.status_code==200 and r.json()['conflict_count']==1
print('API smoke check passed')
