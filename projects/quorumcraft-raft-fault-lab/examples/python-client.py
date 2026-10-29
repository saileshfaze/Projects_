"""Local demonstration client. Start the API before running this script."""
import json
import urllib.request

BASE = "http://127.0.0.1:8080"


def request(path, payload=None):
    body = json.dumps(payload).encode() if payload is not None else None
    headers = {"Content-Type": "application/json"} if body else {}
    with urllib.request.urlopen(urllib.request.Request(BASE + path, data=body, headers=headers), timeout=5) as r:
        return json.load(r)


if __name__ == "__main__":
    request("/tick", {"steps": 35})
    print(request("/commands", {"request_id": "example-1", "op": "put", "key": "units", "value": 12}))
    request("/tick", {"steps": 20})
    print(json.dumps(request("/cluster"), indent=2))
