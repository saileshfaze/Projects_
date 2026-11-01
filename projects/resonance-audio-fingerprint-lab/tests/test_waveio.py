import io
import wave
import numpy as np
import pytest
from resonance.waveio import decode_wav, encode_wav, MAX_BYTES

@pytest.mark.parametrize("rate", [8000, 16000, 44100, 96000])
def test_roundtrip_rates(rate):
    x = np.sin(2*np.pi*440*np.arange(rate//5)/rate)*0.3
    audio = decode_wav(encode_wav(x, rate))
    assert audio.sample_rate == rate and audio.channels == 1
    assert np.max(np.abs(x-audio.samples)) < 1e-4

@pytest.mark.parametrize("payload", [b"", b"random", b"RIFFxxxxWAVEjunk"])
def test_bad_wav(payload):
    with pytest.raises(ValueError): decode_wav(payload)

def test_size_limit():
    with pytest.raises(ValueError, match="size"): decode_wav(b"x"*(MAX_BYTES+1))

def test_stereo_downmix():
    buf = io.BytesIO()
    with wave.open(buf, "wb") as stream:
        stream.setnchannels(2); stream.setsampwidth(2); stream.setframerate(16000)
        stream.writeframes(np.array([10000,-10000,5000,5000], dtype="<i2").tobytes())
    audio = decode_wav(buf.getvalue())
    assert audio.channels == 2 and abs(audio.samples[0]) < 1e-8
    assert audio.samples[1] > 0

def test_invalid_encoding():
    with pytest.raises(ValueError): encode_wav(np.array([np.nan]))

def test_invalid_rate():
    with pytest.raises(ValueError): encode_wav(np.array([0.0]), 500)

def test_silence():
    assert np.max(np.abs(decode_wav(encode_wav(np.zeros(20))).samples)) == 0
