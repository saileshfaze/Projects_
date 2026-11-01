import base64
import pytest
from fastapi.testclient import TestClient
from resonance.api import create_app

@pytest.fixture
def client(tmp_path):
    return TestClient(create_app(str(tmp_path/"test.sqlite")))

def64=lambda raw: base64.b64encode(raw).decode()

def test_health(client):
    assert client.get("/health").json()["status"]=="ok"

def test_ingest_list_search_delete(client, melody):
    response=client.post("/clips",json={"name":"demo","wav_base64":def64(melody)})
    assert response.status_code==201
    clip_id=response.json()["id"]
    assert len(client.get("/clips").json())==1
    assert client.get(f"/clips/{clip_id}").status_code==200
    results=client.post("/search",json={"wav_base64":def64(melody)}).json()["matches"]
    assert results[0]["clip_id"]==clip_id
    assert client.delete(f"/clips/{clip_id}").status_code==200
    assert client.get(f"/clips/{clip_id}").status_code==404

def test_invalid_base64(client):
    assert client.post("/clips",json={"name":"bad","wav_base64":"not-base64!"}).status_code==422

def test_invalid_wav(client):
    assert client.post("/clips",json={"name":"bad","wav_base64":def64(b"not a wav")}).status_code==422

def test_missing_clip(client):
    assert client.delete("/clips/absent").status_code==404

def test_invalid_search_limit(client, melody):
    assert client.post("/search",json={"wav_base64":def64(melody),"limit":0}).status_code==422
