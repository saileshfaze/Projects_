import json
from seismoscope.synthetic import generate
from seismoscope.pipeline import run

def test_determinism():assert generate(seed=42)==generate(seed=42)
def test_seed_changes():assert generate(seed=42)!=generate(seed=43)
def test_output():
    x=run(42)
    assert x['stations']==5
    assert len(x['picks'])>=3
    assert len(x['events'])>=1
    assert x['events'][0]['residual_s']>=0
def test_json():json.dumps(run(4))
