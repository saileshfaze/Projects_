def test_breaking_change():
    from app.core import compare
    assert compare({'id':1},{})['breaking']
    assert not compare({'id':1},{'id':2,'new':True})['breaking']
