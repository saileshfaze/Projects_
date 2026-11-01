"""Verify committed WAV files against their manifest."""
import hashlib
import json
from pathlib import Path
from wave import open as open_wave

root = Path(__file__).resolve().parents[1] / "data"
manifest = json.loads((root / "manifest.json").read_text())
for name, meta in manifest.items():
    raw = (root / name).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == meta["sha256"], name
    with open_wave(str(root / name), "rb") as stream:
        assert stream.getframerate() == meta["sample_rate"]
        assert abs(stream.getnframes()/stream.getframerate()-meta["duration_s"]) < 1e-9
print(f"Verified {len(manifest)} synthetic WAV files")
