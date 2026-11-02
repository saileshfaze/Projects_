import pytest
from vaultline.audit import AuditLog
from vaultline.errors import IntegrityError

def test_chain(tmp_path):
    audit=AuditLog(tmp_path/"audit.sqlite3")
    assert audit.verify() == 0
    audit.append("snapshot", {"files": 2})
    audit.append("verify", {"ok": True})
    assert audit.verify() == 2

def test_tamper(tmp_path):
    audit=AuditLog(tmp_path/"audit.sqlite3")
    audit.append("snapshot", {"files": 2})
    with audit.connect() as c: c.execute("UPDATE events SET payload='{}' WHERE seq=1")
    with pytest.raises(IntegrityError): audit.verify()

def test_sequence_gap(tmp_path):
    audit=AuditLog(tmp_path/"audit.sqlite3")
    audit.append("a", {}); audit.append("b", {})
    with audit.connect() as c: c.execute("DELETE FROM events WHERE seq=1")
    with pytest.raises(IntegrityError): audit.verify()
