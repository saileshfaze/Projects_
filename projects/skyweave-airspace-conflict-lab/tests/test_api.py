import pytest
from fastapi.testclient import TestClient
from skyweave.api import app

client=TestClient(app)

def test_health():assert client.get('/health').json()['status']=='ok'

def test_analyze(crossing_payload):
    res=client.post('/v1/analyze',json=crossing_payload)
    assert res.status_code==200 and res.json()['conflict_count']==1

def test_invalid_threshold(crossing_payload):
    assert client.post('/v1/analyze',json={**crossing_payload,'horizontal_nm':-1}).status_code==422

def test_invalid_callsign(crossing_payload):
    crossing_payload['flights'][0]['callsign']='bad name'
    assert client.post('/v1/analyze',json=crossing_payload).status_code==422

def test_persist(monkeypatch,tmp_path,crossing_payload):
    monkeypatch.setenv('SKYWEAVE_DB',str(tmp_path/'runs.db'))
    res=client.post('/v1/runs',json=crossing_payload)
    assert res.status_code==201
    key=res.json()['run_id']
    assert client.get(f'/v1/runs/{key}').json()['conflict_count']==1
    assert client.get('/v1/runs/unknown').status_code==404
