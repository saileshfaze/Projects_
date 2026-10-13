from app.core import compare, evaluate_samples, fingerprint
from app.drift import drift_summary, ks_distance, lexical_similarity, population_stability_index
from app.schema import changes, infer


def test_removed_required_field_breaks_contract():
    report = compare({"id": 1, "status": "ok"}, {"id": 2})
    assert report["breaking"]
    assert any(change["code"] == "FIELD_REMOVED" for change in report["changes"])


def test_additive_field_is_compatible():
    assert not compare({"id": 1}, {"id": 2, "name": "new"})["breaking"]


def test_optional_to_required_is_safe():
    old = infer([{"id": 1}, {"id": 2, "note": "x"}])
    new = infer([{"id": 3, "note": "y"}])
    assert not any(item["severity"] == "breaking" for item in changes(old, new))


def test_required_to_optional_is_breaking():
    old = infer([{"id": 1, "note": "x"}])
    new = infer([{"id": 2}, {"id": 3, "note": "y"}])
    assert any(item["code"] == "FIELD_BECAME_OPTIONAL" for item in changes(old, new))


def test_nested_array_type_regression():
    assert compare({"items": [{"score": 1}]}, {"items": [{"score": "bad"}]})["breaking"]


def test_empty_array_unknown_is_not_false_break():
    assert not compare({"items": []}, {"items": [1]})["breaking"]


def test_numeric_widening_is_breaking():
    assert compare({"count": 1}, {"count": 1.5})["breaking"]
    assert not compare({"count": 1.5}, {"count": 1})["breaking"]


def test_bool_not_integer():
    assert fingerprint(True)["type"] == "boolean"
    assert compare({"ok": True}, {"ok": 1})["breaking"]


def test_lexical_drift():
    assert lexical_similarity("payment accepted", "payment accepted") == 1.0
    assert lexical_similarity("payment accepted", "access denied") < 0.55
    assert evaluate_samples([{"message": "payment accepted"}], [{"message": "access denied"}])["verdict"] == "fail"


def test_distribution_shift():
    old = [float(i) for i in range(100)]
    new = [float(i + 200) for i in range(100)]
    assert ks_distance(old, new) == 1.0
    assert population_stability_index(old, new) > 0
    assert drift_summary(old, new)["drift_detected"]
