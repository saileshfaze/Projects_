"""Strict, bounded RIFF/WAVE PCM ingestion. No codecs or network calls."""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import io
import wave
import numpy as np

MAX_BYTES = 24 * 1024 * 1024
MAX_SECONDS = 120.0

@dataclass(frozen=True)
class Audio:
    samples: np.ndarray
    sample_rate: int
    channels: int

    @property
    def duration(self) -> float:
        return len(self.samples) / self.sample_rate


def decode_wav(raw: bytes) -> Audio:
    if len(raw) > MAX_BYTES:
        raise ValueError("WAV exceeds size limit")
    if not raw.startswith(b"RIFF") or raw[8:12] != b"WAVE":
        raise ValueError("expected RIFF/WAVE")
    try:
        with wave.open(io.BytesIO(raw), "rb") as stream:
            channels = stream.getnchannels()
            rate = stream.getframerate()
            width = stream.getsampwidth()
            frames = stream.getnframes()
            if channels not in (1, 2) or not 8000 <= rate <= 96000:
                raise ValueError("unsupported channels or sample rate")
            if width not in (1, 2, 3, 4):
                raise ValueError("unsupported PCM width")
            if frames / rate > MAX_SECONDS:
                raise ValueError("WAV exceeds duration limit")
            if stream.getcomptype() != "NONE":
                raise ValueError("compressed WAV is unsupported")
            payload = stream.readframes(frames)
    except (wave.Error, EOFError, OSError) as exc:
        raise ValueError("invalid WAV") from exc
    if width == 1:
        values = (np.frombuffer(payload, dtype=np.uint8).astype(np.float64) - 128) / 128
    elif width == 2:
        values = np.frombuffer(payload, dtype="<i2").astype(np.float64) / 32768
    elif width == 4:
        values = np.frombuffer(payload, dtype="<i4").astype(np.float64) / (2**31)
    else:
        u = np.frombuffer(payload, dtype=np.uint8).reshape(-1, 3).astype(np.int32)
        packed = u[:, 0] | (u[:, 1] << 8) | (u[:, 2] << 16)
        signed = np.where(packed & 0x800000, packed - 0x1000000, packed)
        values = signed.astype(np.float64) / (2**23)
    if len(values) != frames * channels:
        raise ValueError("truncated WAV frames")
    mono = values.reshape(-1, channels).mean(axis=1)
    if not np.isfinite(mono).all():
        raise ValueError("non-finite audio")
    return Audio(mono, rate, channels)


def read_wav(path: str | Path) -> Audio:
    p = Path(path)
    if p.stat().st_size > MAX_BYTES:
        raise ValueError("WAV exceeds size limit")
    return decode_wav(p.read_bytes())


def encode_wav(samples: np.ndarray, sample_rate: int = 16000) -> bytes:
    x = np.asarray(samples, dtype=np.float64)
    if x.ndim != 1 or not np.isfinite(x).all():
        raise ValueError("expected finite mono samples")
    if not 8000 <= sample_rate <= 96000:
        raise ValueError("invalid sample rate")
    pcm = (np.clip(x, -1.0, 1.0) * 32767).astype("<i2")
    out = io.BytesIO()
    with wave.open(out, "wb") as stream:
        stream.setnchannels(1)
        stream.setsampwidth(2)
        stream.setframerate(sample_rate)
        stream.writeframes(pcm.tobytes())
    return out.getvalue()
