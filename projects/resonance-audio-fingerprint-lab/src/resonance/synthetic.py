"""Deterministic, fictional sound clips for regression tests and demos."""
from __future__ import annotations
import numpy as np
from .waveio import encode_wav

RATE = 16000

def make_clip(seed: int = 7, seconds: float = 3.0, variant: str = "melody") -> bytes:
    if not 0.2 <= seconds <= 30:
        raise ValueError("duration out of range")
    rng = np.random.default_rng(seed)
    n = round(RATE * seconds)
    t = np.arange(n) / RATE
    if variant == "melody":
        # Several stable harmonics with rhythmic changes and transients.
        notes = np.array([220, 330, 440, 294, 392, 523, 349, 262], dtype=float)
        freq = notes[np.minimum((t * 4).astype(int) % len(notes), len(notes)-1)]
        phase = np.cumsum(2 * np.pi * freq / RATE)
        gate = 0.65 + 0.35 * np.cos(2*np.pi*2*t)
        x = 0.35 * np.sin(phase) * gate + 0.12 * np.sin(2 * phase) + 0.005 * rng.normal(size=n)
    elif variant == "chirp":
        phase = 2*np.pi*(180*t + 120*t*t)
        x = 0.35*np.sin(phase) + 0.05*np.sin(3*phase)
    elif variant == "noise":
        x = 0.12 * rng.normal(size=n)
    elif variant == "silence":
        x = np.zeros(n)
    else:
        raise ValueError("unknown synthetic variant")
    return encode_wav(x, RATE)
