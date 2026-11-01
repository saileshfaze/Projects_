import numpy as np
import pytest
from resonance.waveio import decode_wav
from resonance.synthetic import make_clip
from resonance.dsp import frame_audio, stft_magnitude, mel_filterbank, log_mel, extract_features, spectral_novelty, hz_to_mel, mel_to_hz

@pytest.mark.parametrize("n", [0, 1, 128, 1024, 2048, 3200])
def test_frames_shape(n):
    frames = frame_audio(np.zeros(n))
    assert frames.shape[1] == 1024
    assert len(frames) == (0 if n == 0 else max(1, 1+(n-1024+255)//256))

def test_stft_empty():
    assert stft_magnitude(np.array([])).shape == (0, 513)

def test_mel_filterbank():
    bank = mel_filterbank(16000)
    assert bank.shape == (32, 513)
    assert np.all(bank >= 0)
    assert np.all(bank.sum(axis=1) > 0)

@pytest.mark.parametrize("freq", [0, 100, 440, 2000, 8000])
def test_mel_inversion(freq):
    assert abs(float(mel_to_hz(hz_to_mel(freq)))-freq) < 1e-7

def test_tone_centroid():
    rate=16000; t=np.arange(rate)/rate
    from resonance.waveio import Audio
    f = extract_features(Audio(0.5*np.sin(2*np.pi*440*t), rate, 1))
    assert 400 < f.spectral_centroid_hz < 500
    assert 0.30 < f.rms < 0.38
    assert f.peak <= 0.5 + 1e-6

def test_silence_features():
    f=extract_features(decode_wav(make_clip(7, 1, "silence")))
    assert f.rms == 0 and f.silence_fraction == 1
    assert f.spectral_flux == 0

def test_log_mel_nonnegative():
    audio=decode_wav(make_clip())
    m=log_mel(audio.samples, audio.sample_rate)
    assert m.shape[1] == 32 and np.all(m>=0)

def test_novelty():
    audio=decode_wav(make_clip())
    novelty=spectral_novelty(audio.samples)
    assert novelty[0] == 0 and np.all(novelty>=0)

def test_invalid_frame():
    with pytest.raises(ValueError): frame_audio(np.ones(5), 0)

def test_invalid_mel():
    with pytest.raises(ValueError): mel_filterbank(0)
