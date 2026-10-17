"""Minimal standard-library client for local testing."""
import json
from pathlib import Path
from urllib.request import Request, urlopen

body = Path("data/demo_scenario.json").read_bytes()
request = Request("http://127.0.0.1:8000/v1/dispatches", data=body,
                  headers={"Content-Type": "application/json"}, method="POST")
with urlopen(request, timeout=30) as response:
    print(json.dumps(json.load(response), indent=2))
