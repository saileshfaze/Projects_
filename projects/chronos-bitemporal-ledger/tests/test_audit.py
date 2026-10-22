from chronos_ledger.audit import verify
from chronos_ledger.db import connect
from chronos_ledger.models import Correction


def event(key, status):
    return Correction(
        valid_from="2026-01-01", valid_to="2027-01-01",
        payload={"status": status}, actor="test", idempotency_key=key,
    )


def test_valid_chain_after_correction(ledger, clock):
    ledger.correct("t", "e", event("a", "open"))
    clock.set("2026-02-01T00:00:00Z")
    ledger.correct("t", "e", event("b", "closed"))
    report = verify(ledger.path, "t")
    assert report.valid, report.problems
    assert report.operations == 2
    assert report.versions == 2


def test_payload_tampering_detected(ledger):
    ledger.correct("t", "e", event("a", "open"))
    conn = connect(ledger.path)
    try:
        conn.execute("UPDATE record_versions SET payload_json=? WHERE tenant=?", ('{"status":"altered"}', "t"))
    finally:
        conn.close()
    report = verify(ledger.path, "t")
    assert not report.valid
    assert any("payload hash mismatch" in issue for issue in report.problems)


def test_chain_tampering_detected(ledger):
    ledger.correct("t", "e", event("a", "open"))
    conn = connect(ledger.path)
    try:
        conn.execute("UPDATE operations SET actor=? WHERE tenant=?", ("mallory", "t"))
    finally:
        conn.close()
    assert not verify(ledger.path, "t").valid
