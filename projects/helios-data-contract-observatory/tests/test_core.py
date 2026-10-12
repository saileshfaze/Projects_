def test_validation():
    from app.core import validate
    assert validate([{'id':1}],{'fields':{'id':'integer'}})['valid']
    assert not validate([{'id':'bad'}],{'fields':{'id':'integer'}})['valid']
