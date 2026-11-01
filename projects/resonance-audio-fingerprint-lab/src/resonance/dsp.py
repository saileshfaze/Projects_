"""Signal transforms and interpretable acoustic descriptors."""
from __future__ import annotations
from dataclasses import dataclass, asdict
import numpy as np
from .waveio import Audio

FRAME = 1024
HOP = 256


def frame_audio(x: np.ndarray, size: int = FRAME, hop: int = HOP) -> np.ndarray:
    if size < 2 or hop < 1:
        raise ValueError("invalid frame configuration")
    x = np.asarray(x, dtype=np.float64)
    if x.ndim != 1:
        raise ValueError("expected mono signal")
    if len(x) == 0:
        return np.empty((0, size), dtype=np.float64)
    n = max(1, 1 + (len(x) - size + hop - 1) // hop)
    target = (n - 1) * hop + size
    padded = np.pad(x, (0, max(0, target - len(x))))
    return np.lib.stride_tricks.sliding_window_view(padded, size)[::hop][:n].copy()


def stft_magnitude(x: np.ndarray, size: int = FRAME, hop: int = HOP) -> np.ndarray:
    frames = frame_audio(x, size, hop)
    if len(frames) == 0:
        return np.empty((0, size // 2 + 1), dtype=np.float64)
    return np.abs(np.fft.rfft(frames * np.hanning(size), axis=1))


def hz_to_mel(hz: np.ndarray | float) -> np.ndarray:
    return 2595 * np.log10(1 + np.asarray(hz) / 700)


def mel_to_hz(mel: np.ndarray | float) -> np.ndarray:
    return 700 * (10 ** (np.asarray(mel) / 2595) - 1)


def mel_filterbank(rate: int, size: int = FRAME, bands: int = 32) -> np.ndarray:
    if bands < 2 or rate <= 0:
        raise ValueError("invalid mel filterbank")
    points = mel_to_hz(np.linspace(0, hz_to_mel(rate / 2), bands + 2))
    freqs = np.fft.rfftfreq(size, 1 / rate)
    bank = np.zeros((bands, len(freqs)))
    for i in range(bands):
        left, middle, right = points[i:i+3]
        bank[i] = np.maximum(0, np.minimum((freqs - left) / max(middle-left, 1e-12), (right-freqs) / max(right-middle, 1e-12)))
    return bank


def log_mel(x: np.ndarray, rate: int, size: int = FRAME, hop: int = HOP, bands: int = 32) -> np.ndarray:
    magnitude = stft_magnitude(x, size, hop)
    return np.log1p((magnitude ** 2) @ mel_filterbank(rate, size, bands).T)


@dataclass(frozen=True)
class Features:
    duration_s: float
    sample_rate: int
    rms: float
    peak: float
    zero_crossing_rate: float
    spectral_centroid_hz: float
    spectral_rolloff_hz: float
    spectral_flux: float
    silence_fraction: float

    def to_dict(self) -> dict:
        return asdict(self)


def extract_features(audio: Audio) -> Features:
    x = audio.samples
    if len(x) == 0:
        raise ValueError("empty audio")
    magnitude = stft_magnitude(x)
    energy = np.sum(magnitude, axis=1)
    freqs = np.fft.rfftfreq(FRAME, 1 / audio.sample_rate)
    centroid = np.sum(magnitude * freqs, axis=1) / np.maximum(energy, 1e-12)
    cumsum = np.cumsum(magnitude, axis=1)
    rolloff_idx = np.argmax(cumsum >= (0.85 * energy[:, None]), axis=1)
    norm = magnitude / np.maximum(np.linalg.norm(magnitude, axis=1, keepdims=True), 1e-12)
    flux = np.maximum(0, np.diff(norm, axis=0)).sum(axis=1)
    frames = frame_audio(x)
    frame_rms = np.sqrt(np.mean(frames**2, axis=1))
    return Features(
        duration_s=round(audio.duration, 6), sample_rate=audio.sample_rate,
        rms=float(np.sqrt(np.mean(x**2))), peak=float(np.max(np.abs(x))),
        zero_crossing_rate=float(np.mean(np.diff(np.signbit(x)))) if len(x) > 1 else 0.0,
        spectral_centroid_hz=float(np.mean(centroid)),
        spectral_rolloff_hz=float(np.mean(freqs[rolloff_idx])),
        spectral_flux=float(np.mean(flux)) if len(flux) else 0.0,
        silence_fraction=float(np.mean(frame_rms < 0.01)),
    )


def spectral_novelty(x: np.ndarray) -> np.ndarray:
    mag = stft_magnitude(x)
    if len(mag) == 0:
        return np.empty(0)
    norm = mag / np.maximum(np.linalg.norm(mag, axis=1, keepdims=True), 1e-12)
    return np.r_[0.0, np.maximum(0, np.diff(norm, axis=0)).sum(axis=1)]
