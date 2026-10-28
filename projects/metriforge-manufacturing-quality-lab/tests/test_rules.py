from metriforge.models import Baseline
from metriforge.rules import shewhart

def test_beyond_3sigma():
    sig=shewhart([0,0,4],Baseline(0,1,20,'test'))
    assert any(x.rule=='beyond_3sigma' and x.index==2 for x in sig)
def test_eight_same_side():
    sig=shewhart([.2]*8,Baseline(0,1,20,'test'))
    assert any(x.rule=='eight_same_side' for x in sig)
def test_six_trending():
    sig=shewhart([0,.1,.2,.3,.4,.5],Baseline(0,1,20,'test'))
    assert any(x.rule=='six_trending' for x in sig)
def test_two_of_three():
    sig=shewhart([2.3,0,2.5],Baseline(0,1,20,'test'))
    assert any(x.rule=='two_of_three_2sigma' for x in sig)
def test_four_of_five():
    sig=shewhart([1.2,1.2,0,1.2,1.2],Baseline(0,1,20,'test'))
    assert any(x.rule=='four_of_five_1sigma' for x in sig)
