import math
import pytest
from thermagrid import Building,Step,simulate,compare_controls

@pytest.fixture
def building():return Building(2,4,3,2,19)

def test_empty(building):
    assert simulate(building,[])['steps']==0

def test_no_energy_off(building):
    assert simulate(building,[Step(0)]*10,mode='off')['energy_kwh']==0

def test_thermostat_heats(building):
    x=simulate(building,[Step(0)]*4);assert x['energy_kwh']>0

def test_ambient_equilibrium():
    b=Building(2,4,0,0,20);assert simulate(b,[Step(20)]*50)['final_temp_c']==20

def test_conservation_one_step():
    b=Building(2,4,0,0,20);x=simulate(b,[Step(12)],dt_hours=1,mode='off')
    assert x['final_temp_c']==19

def test_price(building):
    x=simulate(building,[Step(0,price_per_kwh=.4)]);assert x['cost']==pytest.approx(x['energy_kwh']*.4)

def test_compare(building):
    x=compare_controls(building,[Step(0)]*3);assert x['uncontrolled']['energy_kwh']==0

def test_reproducible(building):
    assert simulate(building,[Step(5)]*3)==simulate(building,[Step(5)]*3)

@pytest.mark.parametrize('r,c,h,cool,t',[(0,1,1,1,20),(1,0,1,1,20),(1,1,-1,1,20),(1,1,1,-1,20),(math.inf,1,1,1,20)])
def test_invalid_building(r,c,h,cool,t):
    with pytest.raises(ValueError):Building(r,c,h,cool,t)

@pytest.mark.parametrize('step', [Step(10),Step(15,1,.3)])
def test_step_types(building,step):assert simulate(building,[step])['steps']==1

@pytest.mark.parametrize('dt',[0,-1,9,math.nan])
def test_invalid_dt(building,dt):
    with pytest.raises(ValueError):simulate(building,[Step(0)],dt_hours=dt)

def test_invalid_mode(building):
    with pytest.raises(ValueError):simulate(building,[],mode='unknown')

def test_invalid_step(building):
    with pytest.raises(TypeError):simulate(building,[{}])

def test_invalid_price():
    with pytest.raises(ValueError):Step(0,price_per_kwh=-1)

def test_cooling():
    b=Building(2,4,3,2,29);assert simulate(b,[Step(35)])['trace'][0]['hvac_kw']==-2
