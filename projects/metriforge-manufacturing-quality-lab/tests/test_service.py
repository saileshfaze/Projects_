from metriforge.service import QualityService

def test_service_end_to_end(tmp_path,scenario,spec):
    svc=QualityService(str(tmp_path/'demo.sqlite'));svc.set_spec(spec)
    a,b,_=scenario
    assert svc.ingest(a)['inserted']==80
    assert svc.ingest(b)['inserted']==120
    assert svc.ingest(b)['replayed']==120
    assert svc.audit()['valid']
    assert svc.report('line-07','press-03','diameter_mm')['production_count']==120
