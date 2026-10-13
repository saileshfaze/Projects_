from app.storage import Store


def test_versioned_snapshots_and_evaluation(tmp_path):
    store = Store(tmp_path / "test.db")
    store.init()
    assert store.snapshot("service", [{"ok": True}])["version"] == 1
    assert store.snapshot("service", [{"ok": False}])["version"] == 2
    assert store.get_snapshot("service", 1)["samples"] == [{"ok": True}]
    assert store.get_snapshot("service")["version"] == 2
    assert len(store.versions("service")) == 2
    run_id = store.record("service", 1, {"verdict": "pass"})
    assert store.evaluation(run_id)["report"]["verdict"] == "pass"
    assert store.evaluation("not-a-uuid") is None
