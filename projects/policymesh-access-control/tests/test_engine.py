import copy
import json
from pathlib import Path
import pytest
from policymesh.engine import evaluate, validate_policy, PolicyError, canonical_report, evaluate_batch

ROOT=Path(__file__).resolve().parents[1]
@pytest.fixture
def policy(): return json.loads((ROOT/'data/policy.json').read_text())
def req(action='read',resource='document:public',role='viewer',clearance=0,mfa=False):
    return {'action':action,'resource':resource,'subject':{'role':role,'clearance':clearance},'environment':{'mfa':mfa}}

def test_public(policy): assert evaluate(policy,req()).allowed
def test_unmatched_default_deny(policy): assert evaluate(policy,req('delete')).reason=='default_deny'
def test_explicit_deny_overrides_allow(policy): assert evaluate(policy,req('read','document:restricted','admin',0)).reason=='explicit_deny'
def test_admin_allowed_high_clearance(policy): assert evaluate(policy,req('read','document:restricted','admin',3)).allowed
def test_mfa_required(policy): assert not evaluate(policy,req('write','document:internal','editor',2)).allowed
def test_editor_mfa(policy): assert evaluate(policy,req('write','document:internal','editor',2,True)).allowed
def test_viewer_write_denied(policy): assert not evaluate(policy,req('write','document:internal','viewer',2,True)).allowed
def test_matched_order(policy): assert evaluate(policy,req('read','document:restricted','admin',0)).matched==('block-restricted-low-clearance','admin-read')
def test_deterministic(policy): assert canonical_report(policy,[req()])==canonical_report(policy,[req()])
def test_empty_batch(policy): assert evaluate_batch(policy,[])==[]
def test_invalid_request(policy):
    with pytest.raises(PolicyError): evaluate(policy,{'action':'read'})
@pytest.mark.parametrize('mutation', [lambda p:p.pop('version'),lambda p:p.update(rules={}),lambda p:p['rules'][0].update(effect='maybe'),lambda p:p['rules'][1].update(id='block-restricted-low-clearance'),lambda p:p['rules'][0].update(actions=[]),lambda p:p['rules'][0].update(when=[{'path':'x','op':'bad','value':1}]),lambda p:p['rules'][0].update(when=[{'path':'x','op':'exists','value':1}]),lambda p:p['rules'][0].update(when=[{'path':'x','op':'in','value':1}])])
def test_invalid_policies(policy,mutation):
    mutation(policy)
    with pytest.raises(PolicyError): validate_policy(policy)
@pytest.mark.parametrize('op,value,actual,expected', [('eq',2,2,True),('ne',2,3,True),('in',[1,2],2,True),('not_in',[1,2],3,True),('gte',2,3,True),('lte',2,1,True),('contains','bc','abcd',True),('exists',False,None,True),('exists',True,2,True),('gte',2,'2',False)])
def test_operators(op,value,actual,expected):
    from policymesh.engine import _predicate
    ctx={} if actual is None else {'a':actual}
    assert _predicate({'path':'a','op':op,'value':value},ctx)==expected
