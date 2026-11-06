import pytest
from ledgerloom.reconcile import reconcile
from ledgerloom.model import LedgerError

def line(i,day="2026-01-01",amount=100,reference=""):
    return {"seq":i,"day":day,"account":"cash","amount":amount,"reference":reference}
def stmt(day="2026-01-01",amount=100,reference=""):
    return {"day":day,"amount":amount,"reference":reference}
def test_exact():
    result=reconcile([line(1,reference="A")],[stmt(reference="A")])
    assert len(result["matched"])==1
    assert not result["unmatched_ledger"]
def test_unmatched():
    result=reconcile([line(1)],[stmt(amount=200)])
    assert len(result["unmatched_statements"])==1
    assert len(result["unmatched_ledger"])==1
def test_ambiguous():
    result=reconcile([line(1),line(2)],[stmt()])
    assert len(result["ambiguous"])==1
    assert len(result["unmatched_ledger"])==2
def test_reference_priority():
    result=reconcile([line(1,reference="B"),line(2,reference="A")],[stmt(reference="A")])
    assert result["matched"][0]["ledger"]["seq"]==2
def test_one_to_one():
    result=reconcile([line(1)],[stmt(),stmt()])
    assert len(result["matched"])==1
    assert len(result["unmatched_statements"])==1
@pytest.mark.parametrize("tolerance",[-1,1.5,"1"])
def test_bad_tolerance(tolerance):
    with pytest.raises(LedgerError):reconcile([],[],tolerance)
def test_date_window():
    assert len(reconcile([line(1)],[stmt(day="2026-01-03")],2)["matched"])==1
    assert len(reconcile([line(1)],[stmt(day="2026-01-04")],2)["matched"])==0
def test_bad_amount():
    with pytest.raises(LedgerError):reconcile([],[stmt(amount="100")])
