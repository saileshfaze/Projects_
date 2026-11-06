import sqlite3
import pytest
from ledgerloom.journal import Journal
from ledgerloom.model import Entry,Posting,LedgerError

def make(i=1,amount=500):
    return Entry(str(i),f"2026-01-{i:02d}","test",(Posting("cash",amount),Posting("sales",-amount)),f"REF-{i}")
def test_post_and_verify(tmp_path):
    j=Journal(tmp_path/"a.sqlite3")
    assert j.post(make())==1
    assert j.verify()
    assert j.trial_balance()=={"cash":500,"sales":-500}
    assert j.head()!="0"*64
    assert j.post(make())==1
    assert len(j.lines())==2

def test_idempotency_conflict(tmp_path):
    j=Journal(tmp_path/"a.sqlite3");j.post(make())
    with pytest.raises(LedgerError):j.post(make(amount=600))
    assert j.verify()
def test_cutoff(tmp_path):
    j=Journal(tmp_path/"a.sqlite3");j.post(make(1));j.post(make(2,700))
    assert j.trial_balance("2026-01-01")["cash"]==500
    assert j.trial_balance()["cash"]==1200
    assert len(j.lines("cash"))==2
@pytest.mark.parametrize("column,value",[("amount",9999),("account","fraud")])
def test_line_tampering(tmp_path,column,value):
    j=Journal(tmp_path/"a.sqlite3");j.post(make())
    with sqlite3.connect(j.path) as db:
        db.execute(f"UPDATE lines SET {column}=? WHERE event_seq=1 AND line_no=0",(value,))
    assert not j.verify()
def test_event_tampering(tmp_path):
    j=Journal(tmp_path/"a.sqlite3");j.post(make())
    with sqlite3.connect(j.path) as db:
        db.execute("UPDATE events SET hash=? WHERE seq=1",("x"*64,))
    assert not j.verify()
def test_chain_multiple(tmp_path):
    j=Journal(tmp_path/"a.sqlite3")
    for i in range(1,30):j.post(make(i))
    assert j.verify()
    assert sum(j.trial_balance().values())==0
