import pytest
from metriforge.store import Store
from metriforge.models import Reading

def test_idempotent_and_audit(tmp_path,scenario):
    db=Store(str(tmp_path/'a.sqlite'));r=scenario[0][0]
    assert db.ingest(r) is True and db.ingest(r) is False
    assert db.verify()['valid'] and db.verify()['events']==1
    db.close()
def test_conflict(tmp_path,scenario):
    db=Store(str(tmp_path/'a.sqlite'));r=scenario[0][0];db.ingest(r)
    with pytest.raises(ValueError):db.ingest(Reading(**{**r.__dict__,'value':r.value+1}))
    db.close()
def test_tamper_detected(tmp_path,scenario):
    db=Store(str(tmp_path/'a.sqlite'));db.ingest(scenario[0][0]);db.db.execute("UPDATE readings SET payload='{}' WHERE seq=1");db.db.commit()
    assert not db.verify()['valid'];db.close()
def test_readings_filtered(tmp_path,scenario):
    db=Store(str(tmp_path/'a.sqlite'))
    for r in scenario[0][:3]+scenario[1][:2]:db.ingest(r)
    assert len(db.readings('line-07','press-03','diameter_mm','baseline'))==3
    db.close()
