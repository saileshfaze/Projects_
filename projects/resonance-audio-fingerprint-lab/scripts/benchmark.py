"""Microbenchmark for reproducibility, not a production latency guarantee."""
import time
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from resonance.synthetic import make_clip
from resonance.waveio import decode_wav
from resonance.fingerprint import fingerprints

for seconds in (1, 3, 8):
    audio = decode_wav(make_clip(7, seconds))
    t0 = time.perf_counter()
    codes = fingerprints(audio)
    print(f"duration={seconds}s landmarks={len(codes)} elapsed_ms={(time.perf_counter()-t0)*1000:.1f}")
