# HTTP API

`GET /health` returns service health. `GET /clips` lists indexed metadata. `GET /clips/{id}` fetches one clip. `DELETE /clips/{id}` deletes metadata and landmarks. `POST /clips` ingests `{ "name": "sample", "wav_base64": "..." }`. `POST /search` accepts `{ "wav_base64": "...", "limit": 5 }` and returns ranked matches.

All audio must be uncompressed integer PCM RIFF/WAVE. Requests over configured model limits or malformed WAV payloads return 422. The service has **no authentication or rate limiting**; bind to localhost and do not expose to the internet without a reverse proxy, auth, quota enforcement, and network isolation.

Example:

```bash
python - <<'PY'
import base64,json
from pathlib import Path
print(json.dumps({"name":"demo","wav_base64":base64.b64encode(Path("data/melody_a.wav").read_bytes()).decode()}))
PY
```
