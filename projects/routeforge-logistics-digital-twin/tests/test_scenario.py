import pytest
from routeforge.optimizer import optimize
from routeforge.scenario import simulate, percentile

def test_reproducible(problem):
    plan = optimize(problem)
    assert simulate(problem, plan, trials=20, seed=7) == simulate(problem, plan, trials=20, seed=7)

def test_zero_jitter_feasible(problem):
    result = simulate(problem, optimize(problem), trials=10, speed_jitter=0, demand_jitter=0)
    assert result["feasibility_rate"] == 1

def test_percentile():
    assert percentile([1, 2, 3], .5) == 2

def test_bad_trials(problem):
    with pytest.raises(ValueError):
        simulate(problem, optimize(problem), trials=0)
