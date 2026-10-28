import pytest
from metriforge.models import Baseline
from metriforge.ewma import ewma
from metriforge.cusum import cusum
REF=Baseline(0,1,30,'test')
def test_ewma_detects_step():assert ewma([0]*10+[2]*20,REF)[1]
def test_ewma_trace_length():assert len(ewma([1,2,3],REF)[0])==3
def test_cusum_detects_step():assert any(s.rule=='cusum_up' for s in cusum([1.5]*20,REF)[1])
def test_cusum_down():assert any(s.rule=='cusum_down' for s in cusum([-1.5]*20,REF)[1])
@pytest.mark.parametrize('lam',[0,-.1,1.1])
def test_bad_lambda(lam):
    with pytest.raises(ValueError):ewma([1],REF,lam=lam)
def test_bad_cusum():
    with pytest.raises(ValueError):cusum([1],REF,k=0)
