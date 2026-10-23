from fastapi.testclient import TestClient
from verityrag.api import create_app

def test_end_to_end(tmp_path):
    with TestClient(create_app(str(tmp_path / "test.db"))) as client:
        assert client.get("/health").json()["status"] == "ok"
        docs = {"documents": [{"id": "ops", "title": "Redis cache", "body": "Redis cache expires after fifteen minutes."}]}
        assert client.post("/v1/documents", json=docs).json()["upserted"] == 1
        query = {"query": "redis cache expires"}
        assert client.post("/v1/search", json=query).json()["hits"][0]["id"] == "ops"
        result = client.post("/v1/answer", json=query).json()
        assert result["citations"][0]["document_id"] == "ops"
        report = client.post("/v1/evaluate", json={"questions": [{"id": "q1", "question": "redis cache expires"}],
                                                   "qrels": {"q1": ["ops"]}, "k": 1}).json()
        assert report["overall"]["recall"] == 1.0

def test_validation(tmp_path):
    with TestClient(create_app(str(tmp_path / "test.db"))) as client:
        assert client.post("/v1/search", json={"query": "x", "k": 0}).status_code == 422
