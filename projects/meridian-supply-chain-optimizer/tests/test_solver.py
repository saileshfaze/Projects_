import pytest
from meridian.model import Route,Scenario
from meridian.solver import optimize

def scenario():
    return Scenario({'A':4,'B':3},{'X':3,'Y':4},(Route('A','X',4,1),Route('A','Y',4,5),Route('B','X',3,4),Route('B','Y',3,1)))

def test_optimum():
    result=optimize(scenario())
    assert (result.fulfilled,result.total_cost)==(7,11)
    assert result.unmet=={'X':0,'Y':0}

def test_zero():
    assert optimize(Scenario({}, {}, ())).total_cost==0

def test_infeasible():
    result=optimize(Scenario({'A':1},{'X':3},(Route('A','X',1,2),)))
    assert (result.fulfilled,result.unmet['X'])==(1,2)

@pytest.mark.parametrize('bad',[
    Scenario({'A':-1},{'X':1},()),
    Scenario({'A':1},{'X':1},(Route('A','X',-1,1),)),
    Scenario({'A':1},{'X':1},(Route('A','X',1,-1),)),
    Scenario({'A':1},{'X':1},(Route('B','X',1,1),)),
    Scenario({'A':1},{'X':1},(Route('A','X',1,1),Route('A','X',1,1))),
])
def test_invalid(bad):
    with pytest.raises(ValueError):optimize(bad)

def test_rerouting():
    s=Scenario({'A':1,'B':1},{'X':1,'Y':1},(Route('A','X',1,1),Route('A','Y',1,2),Route('B','X',1,2),Route('B','Y',1,100)))
    assert optimize(s).total_cost==4

def test_repeatable():
    assert optimize(scenario())==optimize(scenario())
