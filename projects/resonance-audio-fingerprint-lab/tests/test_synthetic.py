import pytest
from resonance.synthetic import make_clip
from resonance.waveio import decode_wav

@pytest.mark.parametrize("variant",["melody","chirp","noise","silence"])
def test_variants(variant):
    a=make_clip(7,1,variant)
    assert a==make_clip(7,1,variant)
    assert decode_wav(a).duration==1

def test_seeds_change_noise():
    assert make_clip(7,1,"noise")!=make_clip(8,1,"noise")

def test_bad_variant():
    with pytest.raises(ValueError): make_clip(7,1,"other")

def test_bad_duration():
    with pytest.raises(ValueError): make_clip(7,0.1)
