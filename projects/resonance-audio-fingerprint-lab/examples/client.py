"""Example API client using only the Python standard library."""
import base64
import json
from pathlib import Path
from urllib.request import Request, urlopen

raw = Path("data/melody_a.wav").read_bytes()
payload = json.dumps({"name": "synthetic-demo", "wav_base64": base64.b64encode(raw).decode()}).encode()
request = Request("http://127.0.0.1:8000/clips", data=payload,
                  headers={"Content-Type": "application/json"}, method="POST")
with urlopen(request, timeout=10) as response:
    print(response.read().decode())
