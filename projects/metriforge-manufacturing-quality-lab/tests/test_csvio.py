import pytest
from metriforge.csvio import save_readings,load_readings

def test_roundtrip(tmp_path,scenario):
    p=str(tmp_path/'a.csv');save_readings(p,scenario[0][:3]);assert load_readings(p)==scenario[0][:3]
def test_bad_header(tmp_path):
    p=tmp_path/'bad.csv';p.write_text('x,y\n1,2\n')
    with pytest.raises(ValueError):load_readings(str(p))
