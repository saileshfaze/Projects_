import pytest
from flagship.core import Flag, Rule, bucket, evaluate, from_dict, load_flags

def flag(**kwargs):
    return Flag('x',{'control':False,'treatment':True},'control',**kwargs)

def test_determinism():
    f=flag(rollout={'treatment':5000})
    assert evaluate(f,'abc')==evaluate(f,'abc')

def test_disabled(): assert evaluate(flag(enabled=False),'a').reason=='disabled'
def test_rule(): assert evaluate(flag(rules=[Rule('country','eq','IT','treatment')]),'a',{'country':'IT'}).value is True
def test_rule_missing(): assert evaluate(flag(rules=[Rule('country','eq','IT','treatment')]),'a').value is False
def test_in(): assert evaluate(flag(rules=[Rule('country','in',['IT'],'treatment')]),'a',{'country':'IT'}).value is True
def test_gte(): assert evaluate(flag(rules=[Rule('age','gte',18,'treatment')]),'a',{'age':19}).value is True
def test_lte(): assert evaluate(flag(rules=[Rule('age','lte',18,'treatment')]),'a',{'age':17}).value is True
def test_bucket_range(): assert all(0<=bucket(flag(),str(i))<10000 for i in range(100))
def test_empty_subject():
    with pytest.raises(ValueError): bucket(flag(),'')
def test_full_rollout(): assert evaluate(flag(rollout={'treatment':10000}),'a').value is True
def test_zero_rollout(): assert evaluate(flag(rollout={'treatment':0}),'a').value is False
def test_overflow():
    with pytest.raises(ValueError):flag(rollout={'treatment':10001}).validate()
def test_negative():
    with pytest.raises(ValueError):flag(rollout={'treatment':-1}).validate()
def test_invalid_variation():
    with pytest.raises(ValueError):flag(rollout={'other':100}).validate()
def test_invalid_rule():
    with pytest.raises(ValueError):flag(rules=[Rule('a','bad',1,'treatment')]).validate()
def test_invalid_default():
    with pytest.raises(ValueError):Flag('x',{},'missing').validate()
def test_load(): assert 'new-checkout' in load_flags('data/flags.json')
def test_salt_changes(): assert any(bucket(flag(salt='v1'),str(i))!=bucket(flag(salt='v2'),str(i)) for i in range(10))
