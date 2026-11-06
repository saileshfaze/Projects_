import pytest
from ledgerloom.model import Entry,Posting,LedgerError

def test_valid():
    e=Entry("x","2026-01-01","test",(Posting("cash",100),Posting("sales",-100)))
    assert sum(p.amount for p in e.postings)==0
@pytest.mark.parametrize("amount",[0,1.5,True,"100",None])
def test_invalid_amount(amount):
    with pytest.raises(LedgerError):Posting("cash",amount)
@pytest.mark.parametrize("day",["bad","2026-02-30",None])
def test_invalid_day(day):
    with pytest.raises(LedgerError):Entry("x",day,"test",(Posting("a",1),Posting("b",-1)))
def test_unbalanced():
    with pytest.raises(LedgerError):Entry("x","2026-01-01","test",(Posting("a",2),Posting("b",-1)))
def test_missing_description():
    with pytest.raises(LedgerError):Entry("x","2026-01-01"," ",(Posting("a",1),Posting("b",-1)))
