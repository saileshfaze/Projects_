"""Landmark audio fingerprints: local spectral peaks and time-frequency pairs.

This is a compact educational implementation, not a production content-ID system.
"""
from __future__ import annotations
from dataclasses import dataclass
from collections import Counter
import hashlib
import numpy as np
from .dsp import stft_magnitude, HOP
from .waveio import Audio

@dataclass(frozen=True)
class Landmark:
    code: str
    frame: int


def spectral_peaks(audio: Audio, min_bin: int = 3, max_peaks_per_frame: int = 4) -> list[tuple[int, int]]:
    if audio.sample_rate != 16000:
        duration = len(audio.samples) / audio.sample_rate
        n = round(duration * 16000)
        canonical = np.interp(np.arange(n) / 16000, np.arange(len(audio.samples)) / audio.sample_rate, audio.samples)
    else:
        canonical = audio.samples
    mag = stft_magnitude(canonical)
    if not len(mag):
        return []
    # Normalize each frame to avoid treating low-level noise as reliable landmarks.
    logmag = np.log1p(mag)
    result = []
    for t in range(1, len(logmag)-1):
        row = logmag[t]
        threshold = max(float(np.quantile(row, 0.90)), 0.3)
        indices = np.where((row[1:-1] > row[:-2]) & (row[1:-1] >= row[2:]) & (row[1:-1] >= threshold))[0] + 1
        indices = indices[indices >= min_bin]
        indices = sorted(indices, key=lambda i: (-row[i], i))[:max_peaks_per_frame]
        result.extend((t, int(i)) for i in sorted(indices))
    return result


def fingerprints(audio: Audio, fanout: int = 4, min_delta: int = 1, max_delta: int = 12) -> list[Landmark]:
    if fanout < 1 or min_delta < 1 or max_delta < min_delta:
        raise ValueError("invalid fingerprint parameters")
    peaks = spectral_peaks(audio)
    result: list[Landmark] = []
    for i, (t, f) in enumerate(peaks):
        emitted = 0
        for t2, f2 in peaks[i+1:]:
            dt = t2 - t
            if dt > max_delta:
                break
            if dt < min_delta:
                continue
            # Stable across Python versions and processes; compact deterministic code.
            code = hashlib.blake2s(f"{f}:{f2}:{dt}".encode(), digest_size=8).hexdigest()
            result.append(Landmark(code, t))
            emitted += 1
            if emitted >= fanout:
                break
    return result


def match_offsets(query: list[Landmark], reference: list[Landmark]) -> dict:
    """Histogram alignment: reference_frame - query_frame, avoiding Cartesian explosion."""
    by_code: dict[str, list[int]] = {}
    for item in reference:
        by_code.setdefault(item.code, []).append(item.frame)
    votes: Counter[int] = Counter()
    matched = 0
    for item in query:
        for frame in by_code.get(item.code, [])[:100]:
            votes[frame - item.frame] += 1
            matched += 1
    offset, best = sorted(votes.items(), key=lambda kv: (-kv[1], abs(kv[0]), kv[0]))[0] if votes else (0, 0)
    return {"offset_frames": offset, "offset_seconds": round(offset * HOP / 16000, 6),
            "aligned_votes": best, "total_votes": matched,
            "confidence": round(best / max(len(query), 1), 6)}
