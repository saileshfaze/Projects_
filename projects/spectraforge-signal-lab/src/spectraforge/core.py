"""Deterministic DSP primitives for educational synthetic time series."""
from __future__ import annotations
import cmath
import math
import random
from dataclasses import dataclass, asdict

@dataclass(frozen=True)
class Peak:
    frequency_hz: float
    amplitude: float

def fft(samples: list[complex]) -> list[complex]:
    """Radix-2 Cooley-Tukey FFT; length must be a positive power of two."""
    n = len(samples)
    if n == 0 or n & (n - 1):
        raise ValueError("FFT length must be a positive power of two")
    if n == 1:
        return [complex(samples[0])]
    evens = fft(samples[::2]); odds = fft(samples[1::2])
    result = [0j] * n
    for k in range(n // 2):
        t = cmath.exp(-2j * math.pi * k / n) * odds[k]
        result[k] = evens[k] + t
        result[k + n // 2] = evens[k] - t
    return result

def hann(n: int) -> list[float]:
    if n < 2:
        raise ValueError("window length must be at least two")
    return [0.5 - 0.5 * math.cos(2 * math.pi * i / (n - 1)) for i in range(n)]

def spectrum(samples: list[float], sample_rate: float, window: str = "hann") -> list[Peak]:
    n = len(samples)
    if sample_rate <= 0 or n < 2 or n & (n - 1):
        raise ValueError("positive sample rate and power-of-two length >= 2 required")
    if any(not math.isfinite(v) for v in samples):
        raise ValueError("samples must be finite")
    if window not in ("hann", "rectangular"):
        raise ValueError("unknown window")
    weights = hann(n) if window == "hann" else [1.0] * n
    coherent_gain = sum(weights)
    bins = fft([complex(x * weight) for x, weight in zip(samples, weights)])
    return [Peak(k * sample_rate / n, abs(bins[k]) * (1 if k in (0, n // 2) else 2) / coherent_gain) for k in range(n // 2 + 1)]

def dominant_peaks(samples: list[float], sample_rate: float, count: int = 3, window: str = "hann") -> list[Peak]:
    if count < 1:
        raise ValueError("count must be positive")
    bins = spectrum(samples, sample_rate, window)
    candidates = [p for i, p in enumerate(bins) if i > 0 and (i == len(bins) - 1 or p.amplitude >= bins[i + 1].amplitude) and p.amplitude >= bins[i - 1].amplitude]
    return sorted(candidates, key=lambda p: (-p.amplitude, p.frequency_hz))[:count]

def generate_signal(n: int, sample_rate: float, tones: list[tuple[float, float]], noise: float = 0, seed: int = 42) -> list[float]:
    if n < 2 or n & (n - 1) or sample_rate <= 0 or noise < 0:
        raise ValueError("invalid signal parameters")
    if any(f < 0 or f >= sample_rate / 2 or a < 0 for f, a in tones):
        raise ValueError("tones must be below Nyquist with nonnegative amplitudes")
    rng = random.Random(seed)
    return [sum(a * math.sin(2 * math.pi * f * i / sample_rate) for f, a in tones) + rng.gauss(0, noise) for i in range(n)]

def detect_anomalies(samples: list[float], window: int = 16, threshold: float = 4.0) -> list[int]:
    """Past-only rolling z-score; excludes current point from baseline."""
    if window < 2 or threshold <= 0:
        raise ValueError("invalid detector settings")
    indices = []
    for i in range(window, len(samples)):
        history = samples[i-window:i]
        mean = sum(history) / window
        variance = sum((x-mean)**2 for x in history) / window
        if abs(samples[i] - mean) > threshold * max(math.sqrt(variance), 1e-9):
            indices.append(i)
    return indices
