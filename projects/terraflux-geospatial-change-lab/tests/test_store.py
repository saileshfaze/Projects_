from terraflux.store import ReportStore


def test_idempotent_storage(tmp_path):
    store = ReportStore(tmp_path/'reports.sqlite3')
    run = store.put('demo', {'summary': {'changed': 5}})
    assert store.put('demo', {'summary': {'changed': 5}}) == run
    assert len(store.list_runs()) == 1
    assert store.get(run)['summary']['changed'] == 5


def test_different_dataset_changes_id(tmp_path):
    store = ReportStore(tmp_path/'reports.sqlite3')
    assert store.put('one', {'x':1}) != store.put('two', {'x':1})
