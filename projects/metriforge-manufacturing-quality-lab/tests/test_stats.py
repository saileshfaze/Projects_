import pytest
from metriforge.stats import baseline,capability,defect_rate,pearson

def test_baseline_robust_to_outlier():
    b=baseline([1,1.1,1.2,1.3,1.1,1.2,1.4,100]);assert b.center<2

def test_baseline_requires_data():
    with pytest.raises(ValueError):baseline([1,2])
def test_constant_baseline_rejected():
    with pytest.raises(ValueError):baseline([1]*10)
def test_capability_short_null(spec): assert capability([50]*8,spec)['cp'] is None
def test_capability_positive(spec):
    c=capability([50+(-1)**i*.2 for i in range(30)],spec);assert c['cp']>0 and c['ppk']>0
def test_defect_fraction(spec):assert defect_rate([47,48,52,53],spec)==.5
def test_pearson(): assert pearson([1,2,3],[2,4,6])==pytest.approx(1)
def test_pearson_constant():assert pearson([1,1,1],[1,2,3]) is None
