from voltpilot.storage import store,fetch,list_runs
from voltpilot.dispatch import simulate


def test_store_and_fetch(tmp_path,profile,site):
    db=tmp_path/"runs.db"
    summary,steps=simulate(profile,site)
    rid=store(db,site,summary,steps)
    item=fetch(db,rid)
    assert item["audit_valid"] is True
    assert item["summary"]["intervals"]==len(profile)
    assert len(list_runs(db))==1


def test_idempotent_storage(tmp_path,profile,site):
    db=tmp_path/"runs.db"
    summary,steps=simulate(profile,site)
    assert store(db,site,summary,steps)==store(db,site,summary,steps)
    assert len(list_runs(db))==1


def test_missing_run(tmp_path):
    assert fetch(tmp_path/"runs.db","nonexistent") is None
