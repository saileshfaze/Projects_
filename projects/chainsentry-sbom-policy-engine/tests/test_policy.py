from datetime import date
import pytest
from chainsentry import scan
from chainsentry.policy import canonical_digest, PolicyError
from chainsentry.parser import parse_sbom


def inputs(fixture_data):
    return fixture_data("cyclonedx.json"), fixture_data("advisories.json"), fixture_data("policy.json")


def test_expected_failures(fixture_data):
    report = scan(*inputs(fixture_data), today=date(2026, 10, 26))
    assert report.status == "fail"
    assert report.total_components == 6
    assert report.reachable_components == 5
    assert report.summary == {"total": 3, "active": 3, "exempted": 0, "unreachable": 1}
    assert {f.kind for f in report.findings} == {"license", "vulnerability"}


def test_unreachable_does_not_fail_by_default(fixture_data):
    sbom, feed, policy = inputs(fixture_data)
    policy["deny_licenses"] = []
    feed["advisories"] = [a for a in feed["advisories"] if a["id"] == "DEMO-2026-0002"]
    assert scan(sbom, feed, policy).status == "pass"
    policy["fail_unreachable"] = True
    assert scan(sbom, feed, policy).status == "fail"


def test_exemption_and_expiry(fixture_data):
    sbom, feed, policy = inputs(fixture_data)
    policy["deny_licenses"] = []
    policy["exemptions"] = fixture_data("policy-exemption.json")["exemptions"]
    assert scan(sbom, feed, policy, today=date(2026, 10, 26)).status == "pass"
    assert scan(sbom, feed, policy, today=date(2027, 1, 2)).status == "fail"


def test_exemption_missing_reason_rejected(fixture_data):
    sbom, feed, policy = inputs(fixture_data)
    policy["exemptions"] = [{"advisory": "DEMO-2026-0001", "purl": "pkg:pypi/cipherleaf@0.8.1", "expires": "2027-01-01"}]
    with pytest.raises(PolicyError):
        scan(sbom, feed, policy)


def test_digest_stable_across_input_order(fixture_data):
    sbom = fixture_data("cyclonedx.json")
    digest = canonical_digest(parse_sbom(sbom))
    sbom["components"].reverse()
    sbom["dependencies"].reverse()
    assert digest == canonical_digest(parse_sbom(sbom))


def test_missing_metadata_findings(fixture_data):
    sbom, feed, policy = inputs(fixture_data)
    sbom["components"][0]["purl"] = ""
    sbom["components"][0]["licenses"] = []
    assert {f.rule for f in scan(sbom, feed, policy).findings} >= {"missing-license", "missing-purl"}


def test_invalid_threshold(fixture_data):
    sbom, feed, policy = inputs(fixture_data)
    policy["fail_at"] = "extreme"
    with pytest.raises(PolicyError):
        scan(sbom, feed, policy)


def test_all_finding_ids_stable(fixture_data):
    r1 = scan(*inputs(fixture_data)).to_dict()
    r2 = scan(*inputs(fixture_data)).to_dict()
    assert r1 == r2
