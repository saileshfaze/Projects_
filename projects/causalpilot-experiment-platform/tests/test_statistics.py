import math
from causalpilot.statistics import analyze, bootstrap_difference, cuped, srm_test


def test_srm_perfect_balance():
    result=srm_test(500,500,0.5)
    assert result["chi_square"]==0 and result["p_value"]==1


def test_srm_flags_large_imbalance():
    assert srm_test(900,100,0.5)["flag"] is True


def test_srm_empty():
    assert srm_test(0,0,0.5)["p_value"] is None


def test_cuped_no_variance():
    a=[{"revenue":1,"preperiod_revenue":5}]
    b=[{"revenue":2,"preperiod_revenue":5}]
    aa,bb,theta=cuped(a,b)
    assert theta==0 and aa==[1] and bb==[2]


def test_cuped_reduces_covariate_noise():
    a=[{"revenue":i*3+1,"preperiod_revenue":i} for i in range(10)]
    b=[{"revenue":i*3+3,"preperiod_revenue":i} for i in range(10)]
    aa,bb,theta=cuped(a,b)
    assert math.isclose(theta,3)
    assert math.isclose(sum(bb)/10-sum(aa)/10,2)


def test_bootstrap_is_reproducible():
    x=bootstrap_difference([1,2,3],[4,5,6],0.05,seed=3,draws=100)
    assert x==bootstrap_difference([1,2,3],[4,5,6],0.05,seed=3,draws=100)
    assert x["difference"]==3


def test_report_warns_on_missing():
    rows=[{"arm":"A","revenue":1,"preperiod_revenue":2,"converted":1,"refunded":0},
          {"arm":"B","revenue":2,"preperiod_revenue":2,"converted":1,"refunded":0}]
    result=analyze(rows,{"A":100,"B":100},0.5,minimum_per_arm=10)
    assert not result["eligible"] and len(result["warnings"])==2
