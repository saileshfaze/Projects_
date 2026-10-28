import pytest
from metriforge.models import Reading,QualitySpec,Baseline

def test_spec_valid(spec): assert spec.target==50
@pytest.mark.parametrize('a,b,t',[(52,48,50),(48,52,53),(50,50,50)])
def test_spec_invalid(a,b,t):
    with pytest.raises(ValueError):QualitySpec('m',a,b,t)
def test_naive_timestamp_rejected():
    with pytest.raises(ValueError):Reading('x','2026-01-01T00:00:00','L','M','x','lot',1)
def test_nonfinite_rejected():
    with pytest.raises(ValueError):Reading('x','2026-01-01T00:00:00Z','L','M','x','lot',float('nan'))
def test_invalid_baseline():
    with pytest.raises(ValueError):Baseline(0,0,8,'mad')
