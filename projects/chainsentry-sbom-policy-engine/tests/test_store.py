from chainsentry import scan
from chainsentry.store import ScanStore, diff_reports


def test_append_only_history(tmp_path, fixture_data):
    store = ScanStore(tmp_path / "scans.db")
    report = scan(fixture_data("cyclonedx.json"), fixture_data("advisories.json"), fixture_data("policy.json"))
    a = store.save("shop", report)
    b = store.save("shop", report)
    assert b == a + 1
    assert [row["id"] for row in store.history("shop")] == [b, a]
    assert store.get(a)["report"] == report.to_dict()
    assert store.get(999) is None


def test_diff_detects_resolved(tmp_path, fixture_data):
    sbom, feed, policy = (fixture_data(x) for x in ("cyclonedx.json", "advisories.json", "policy.json"))
    before = scan(sbom, feed, policy).to_dict()
    feed["advisories"] = []
    after = scan(sbom, feed, policy).to_dict()
    diff = diff_reports(before, after)
    assert len(diff["resolved"]) == 2
    assert diff["added"] == []


def test_diff_detects_exemption_change(fixture_data):
    sbom, feed, policy = (fixture_data(x) for x in ("cyclonedx.json", "advisories.json", "policy.json"))
    before = scan(sbom, feed, policy).to_dict()
    policy["exemptions"] = fixture_data("policy-exemption.json")["exemptions"]
    after = scan(sbom, feed, policy).to_dict()
    assert len(diff_reports(before, after)["changed"]) == 1


def test_history_limit_validation(tmp_path):
    store = ScanStore(tmp_path / "scans.db")
    import pytest
    with pytest.raises(ValueError):
        store.history("shop", 0)
