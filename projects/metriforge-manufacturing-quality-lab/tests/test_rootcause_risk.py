import pytest
from metriforge.rootcause import rank_covariates
from metriforge.risk import lot_risk

def test_rank_covariates():
    out=rank_covariates([1,2,3,4],{'temperature':[2,4,6,8],'constant':[1]*4})
    assert len(out)==1 and out[0]['name']=='temperature'
def test_hold_risk(): assert lot_risk(.5,3,0,10)['tier']=='hold'
def test_monitor_risk(): assert lot_risk(0,0,0,10)['tier']=='monitor'
def test_bad_risk():
    with pytest.raises(ValueError):lot_risk(1.2,0,0,10)
