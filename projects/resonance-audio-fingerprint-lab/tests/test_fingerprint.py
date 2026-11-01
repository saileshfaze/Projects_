import pytest
from resonance.waveio import decode_wav, encode_wav
from resonance.synthetic import make_clip
from resonance.fingerprint import fingerprints, match_offsets, spectral_peaks, Landmark
import numpy as np

def test_deterministic(melody):
    a=decode_wav(melody)
    assert fingerprints(a) == fingerprints(a)
    assert len(fingerprints(a)) > 100

def test_self_alignment(melody):
    f=fingerprints(decode_wav(melody))
    m=match_offsets(f,f)
    assert m["offset_frames"] == 0
    assert m["aligned_votes"] > 0

def test_shift_alignment():
    ref=[Landmark("a", 12),Landmark("b", 15),Landmark("c", 19)]
    query=[Landmark("a", 2),Landmark("b", 5),Landmark("c", 9)]
    assert match_offsets(query,ref)["offset_frames"] == 10

def test_no_overlap():
    assert match_offsets([Landmark("a",1)], [Landmark("b",2)])["aligned_votes"] == 0

def test_silence_no_peaks():
    assert not fingerprints(decode_wav(make_clip(7,1,"silence")))

def test_peaks_sorted(melody):
    peaks=spectral_peaks(decode_wav(melody))
    assert peaks == sorted(peaks)

def test_rate_resampling():
    t=np.arange(2*8000)/8000
    clip=encode_wav(0.4*np.sin(2*np.pi*440*t),8000)
    assert len(fingerprints(decode_wav(clip))) > 0

@pytest.mark.parametrize("fanout,min_delta,max_delta", [(0,1,12),(4,0,12),(4,10,2)])
def test_bad_parameters(melody, fanout, min_delta, max_delta):
    with pytest.raises(ValueError): fingerprints(decode_wav(melody),fanout,min_delta,max_delta)
