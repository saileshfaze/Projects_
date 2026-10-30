import sqlite3
from skyweave.persistence import Store,digest,canonical

def test_store_idempotent(tmp_path):
    s=Store(str(tmp_path/'a.db'));a={'x':1};b={'y':2}
    key=s.save(a,b)
    assert key==s.save(a,b) and s.load(key)==b and s.verify()
    with s.connect() as db:assert db.execute('SELECT COUNT(*) FROM audit').fetchone()[0]==1

def test_store_multiple_runs(tmp_path):
    s=Store(str(tmp_path/'a.db'))
    s.save({'x':1},{'y':1});s.save({'x':2},{'y':2})
    assert s.verify()
    with s.connect() as db:assert db.execute('SELECT COUNT(*) FROM audit').fetchone()[0]==2

def test_tampered_chain(tmp_path):
    s=Store(str(tmp_path/'a.db'));s.save({'x':1},{'y':2})
    with s.connect() as db:db.execute("UPDATE audit SET action='bad' WHERE seq=1")
    assert not s.verify()

def test_tampered_report(tmp_path):
    s=Store(str(tmp_path/'a.db'));key=s.save({'x':1},{'y':2})
    with s.connect() as db:db.execute("UPDATE runs SET report='{}' WHERE id=?",(key,))
    assert not s.verify()

def test_missing(tmp_path):assert Store(str(tmp_path/'a.db')).load('missing') is None

def test_canonical_order():assert canonical({'b':2,'a':1})==canonical({'a':1,'b':2})
