from skyweave.service import analyze

def test_service(crossing_payload):
    result=analyze(crossing_payload,samples=5)
    assert result['flight_count']==4 and result['conflict_count']==1
    assert result['risk']['samples']==5

def test_service_without_risk(crossing_payload):
    assert 'risk' not in analyze(crossing_payload)
