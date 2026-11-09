import pytest
from hydrograph.scenarios import simulate,scaled,pipe_outage

def test_simulation(network):
    x=simulate(network,seed=7,trials=10);assert x['trials']==10 and len(x['samples'])==10
def test_reproducible(network):assert simulate(network,seed=4,trials=5)==simulate(network,seed=4,trials=5)
def test_scaled(network):assert scaled(network,{'A':2}).demands['A']==4
def test_invalid_scale(network):
    with pytest.raises(ValueError):scaled(network,{'A':-1})
def test_missing_pipe(network):
    with pytest.raises(ValueError):pipe_outage(network,'missing')
def test_outage(network):assert len(pipe_outage(network,'A-C').pipes)==len(network.pipes)-1
def test_invalid_trials(network):
    with pytest.raises(ValueError):simulate(network,trials=0)
def test_seed_variation(network):assert simulate(network,seed=1,trials=5)!=simulate(network,seed=2,trials=5)
