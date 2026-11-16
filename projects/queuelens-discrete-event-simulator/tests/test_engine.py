import pytest
from queuelens.engine import simulate,validate,percentile

def test_empty():
    r=simulate({'servers':2,'jobs':[]});assert r['accepted']==0 and r['utilization']==[0,0]
def test_parallel():
    r=simulate({'servers':2,'jobs':[{'id':'a','arrival':0,'duration':2},{'id':'b','arrival':0,'duration':3}]})
    assert r['accepted']==2 and r['mean_wait']==0 and r['makespan']==3
def test_fifo():
    r=simulate({'servers':1,'jobs':[{'id':'a','arrival':0,'duration':3},{'id':'b','arrival':1,'duration':1},{'id':'c','arrival':2,'duration':1}]})
    assert [x['wait'] for x in r['jobs']]==[0,2,2]
def test_reject():
    r=simulate({'servers':1,'waiting_capacity':0,'jobs':[{'id':'a','arrival':0,'duration':2},{'id':'b','arrival':1,'duration':1}]})
    assert r['rejected']==['b']
def test_finish_before_arrival():
    r=simulate({'servers':1,'waiting_capacity':0,'jobs':[{'id':'a','arrival':0,'duration':1},{'id':'b','arrival':1,'duration':1}]})
    assert r['accepted']==2
def test_zero_duration():
    r=simulate({'servers':1,'jobs':[{'id':'a','arrival':0,'duration':0}]})
    assert r['utilization']==[0]
def test_percentile():assert percentile([0,10],.95)==pytest.approx(9.5)
def test_determinism():
    s={'servers':1,'jobs':[{'id':'a','arrival':0,'duration':1}]};assert simulate(s)==simulate(s)
@pytest.mark.parametrize('scenario',[{'servers':0,'jobs':[]},{'servers':True,'jobs':[]},{'servers':1,'waiting_capacity':-1,'jobs':[]},{'servers':1,'jobs':{}},{'servers':1,'jobs':[{'id':'a','arrival':-1,'duration':1}]},{'servers':1,'jobs':[{'id':'a','arrival':0,'duration':float('nan')}]},{'servers':1,'jobs':[{'id':'a','arrival':0,'duration':1},{'id':'a','arrival':1,'duration':1}]}])
def test_invalid(scenario):
    with pytest.raises(ValueError):validate(scenario)
