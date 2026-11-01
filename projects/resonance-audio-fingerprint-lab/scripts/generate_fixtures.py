"""Generate deterministic audio assets, metadata and spectrogram previews."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from resonance.synthetic import make_clip
from resonance.waveio import decode_wav
from resonance.report import spectrogram_svg

ROOT = Path(__file__).resolve().parents[1]


def generate() -> dict[str, bytes]:
    clips = {"melody_a.wav": make_clip(7, 3, "melody"),
             "melody_b.wav": make_clip(11, 3, "melody"),
             "chirp.wav": make_clip(7, 3, "chirp"),
             "noise.wav": make_clip(7, 3, "noise"),
             "silence.wav": make_clip(7, 1, "silence")}
    manifest = {name: {"sha256": hashlib.sha256(raw).hexdigest(),
                       "duration_s": decode_wav(raw).duration, "sample_rate": 16000}
                for name, raw in sorted(clips.items())}
    outputs = {f"data/{name}": raw for name, raw in clips.items()}
    outputs["data/manifest.json"] = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode()
    outputs["assets/melody-spectrogram.svg"] = spectrogram_svg(decode_wav(clips["melody_a.wav"])).encode()
    return outputs


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    expected = generate()
    mismatches = []
    for name, content in expected.items():
        path = ROOT / name
        if args.check:
            if not path.exists() or path.read_bytes() != content:
                mismatches.append(name)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
    if mismatches:
        print("Outdated fixtures:", ", ".join(mismatches))
        return 1
    print(f"{'Validated' if args.check else 'Generated'} {len(expected)} reproducible fixtures")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
