import pytest
from metriforge.engine import evaluate

def test_report(scenario,spec):
    a,b,_=scenario;r=evaluate(a,b,spec)
    assert r['production_count']==120 and len(r['lots'])==3 and r['signals']
def test_mixed_assets_rejected(scenario,spec):
    a,b,_=scenario
    from metriforge.models import Reading
    b=[Reading(**{**b[0].__dict__,'machine':'other'})]+b[1:]
    with pytest.raises(ValueError):evaluate(a,b,spec)
def test_empty_rejected(scenario,spec):
    with pytest.raises(ValueError):evaluate(scenario[0],[],spec)
def test_sorted_signals(scenario,spec):
    r=evaluate(*scenario[:2],spec)
    assert [s['index'] for s in r['signals']]==sorted(s['index'] for s in r['signals'])
