from fastapi.testclient import TestClient
from metriforge.api import create_app

def test_health(tmp_path):
    with TestClient(create_app(str(tmp_path/'api.sqlite'))) as client:
        assert client.get('/health').json()=={'status':'ok'}
def test_spec_and_ingest(tmp_path,scenario):
    with TestClient(create_app(str(tmp_path/'api.sqlite'))) as client:
        body={'metric':'diameter_mm','lsl':48,'usl':52,'target':50,'unit':'mm'}
        assert client.put('/specs/diameter_mm',json=body).status_code==200
        assert client.post('/readings',json={'readings':[scenario[0][0].__dict__]}).json()['inserted']==1
        assert client.get('/audit').json()['valid']
def test_bad_spec(tmp_path):
    with TestClient(create_app(str(tmp_path/'api.sqlite'))) as client:
        assert client.put('/specs/x',json={'metric':'x','lsl':5,'usl':1,'target':2}).status_code==422
