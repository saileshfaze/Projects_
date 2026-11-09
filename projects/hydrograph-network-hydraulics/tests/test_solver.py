import pytest
from hydrograph.solver import solve,continuity
from hydrograph.model import Network,Pipe

def test_converges(network):
    result=solve(network);assert result.converged and result.residual<1e-8
def test_continuity(network):
    assert max(abs(x) for x in continuity(network,solve(network)).values())<1e-8
def test_reservoir_head(network):assert solve(network).heads['R']==70
def test_single_pipe():
    n=Network('R',50,{'A':2},(Pipe('p','R','A',3),))
    result=solve(n);assert result.converged
    assert result.flows['p']==pytest.approx(2,abs=1e-6)
    assert result.heads['A']==pytest.approx(38,abs=1e-5)
def test_zero_demand():
    n=Network('R',50,{'A':0},(Pipe('p','R','A',3),))
    assert solve(n).converged
def test_invalid_tolerance(network):
    with pytest.raises(ValueError):solve(network,tolerance=0)
def test_max_iter(network):assert solve(network,max_iterations=1).iterations<=1
def test_reproducible(network):assert solve(network)==solve(network)
