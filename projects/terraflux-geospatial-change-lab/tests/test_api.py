from fastapi.testclient import TestClient
from terraflux.api import create_app
from terraflux.synthetic import generate


def test_api_end_to_end(tmp_path):
    root = tmp_path/'data'
    generate(root, 'demo', size=32)
    client = TestClient(create_app(root, tmp_path/'state'/'runs.sqlite3'))
    assert client.get('/health').json()['status'] == 'ok'
    assert client.get('/datasets').json()['datasets'] == ['demo']
    response = client.post('/analyze', json={'dataset_id': 'demo'})
    assert response.status_code == 200, response.text
    run = response.json()['run_id']
    assert client.get(f'/reports/{run}').json()['summary']['valid_pixels'] > 0
    assert len(client.get('/reports').json()['runs']) == 1


def test_api_rejects_traversal(tmp_path):
    client = TestClient(create_app(tmp_path, tmp_path/'state.sqlite3'))
    assert client.post('/analyze', json={'dataset_id': '../etc'}).status_code == 422
    assert client.get('/reports/not-a-run').status_code == 404


def test_api_missing_dataset(tmp_path):
    client = TestClient(create_app(tmp_path, tmp_path/'state.sqlite3'))
    assert client.post('/analyze', json={'dataset_id': 'missing'}).status_code == 422
