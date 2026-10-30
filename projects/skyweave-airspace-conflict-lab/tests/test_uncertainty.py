import pytest
from skyweave.uncertainty import sample_risk

def test_deterministic(crossing_flights):
    a=sample_risk(crossing_flights,samples=12,seed=7)
    b=sample_risk(crossing_flights,samples=12,seed=7)
    assert a==b

def test_probability_bounds(crossing_flights):
    r=sample_risk(crossing_flights,samples=20)
    assert all(0<=v<=1 for v in r.pair_probabilities.values())

def test_zero_sigma_exact(crossing_flights):
    r=sample_risk(crossing_flights,samples=10,horizontal_sigma_m=0,vertical_sigma_ft=0)
    assert r.pair_probabilities=={'SW101|SW202':1.0}
@pytest.mark.parametrize('samples',[0,-1,5001])
def test_invalid_samples(crossing_flights,samples):
    with pytest.raises(ValueError):sample_risk(crossing_flights,samples=samples)
def test_invalid_sigma(crossing_flights):
    with pytest.raises(ValueError):sample_risk(crossing_flights,horizontal_sigma_m=-1)
