from routeforge.storage import save_plan, load_plan

def test_roundtrip(tmp_path):
    path = str(tmp_path / "plans.db")
    save_plan(path, {"plan_id": "abc", "total_cost": 12.5})
    assert load_plan(path, "abc")["total_cost"] == 12.5
    save_plan(path, {"plan_id": "abc", "total_cost": 999})
    assert load_plan(path, "abc")["total_cost"] == 12.5

def test_missing(tmp_path):
    assert load_plan(str(tmp_path / "missing.db"), "unknown") is None
