"""In-process FastAPI smoke check; does not require a running server."""
from fastapi.testclient import TestClient
from quorumcraft.api import create_app
from quorumcraft import Cluster


def main():
    client = TestClient(create_app(Cluster(seed=42)))
    assert client.get("/health").status_code == 200
    assert client.post("/tick", json={"steps": 35}).status_code == 200
    assert client.post("/commands", json={"request_id": "smoke-1", "op": "put", "key": "stock", "value": 8}).status_code == 200
    client.post("/tick", json={"steps": 25})
    assert all(node["state"].get("stock") == 8 for node in client.get("/cluster").json()["nodes"])
    print("In-process FastAPI smoke test passed")


if __name__ == "__main__":
    main()
