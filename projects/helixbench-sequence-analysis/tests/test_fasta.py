import pytest
from helixbench.fasta import parse_fasta

def test_records():
    records = parse_fasta([">alpha description", "ac", "gt", ">beta", "NN"])
    assert [(x.identifier,x.sequence) for x in records] == [("alpha","ACGT"),("beta","NN")]
def test_blank_lines(): assert parse_fasta(["",">a","AC", ""])[0].sequence == "AC"
def test_missing_header():
    with pytest.raises(ValueError): parse_fasta(["ATG"])
def test_duplicate():
    with pytest.raises(ValueError): parse_fasta([">a","ATG",">a","CCC"])
def test_empty_header():
    with pytest.raises(ValueError): parse_fasta([">", "ATG"])
def test_empty_record():
    with pytest.raises(ValueError): parse_fasta([">a",">b","ATG"])
def test_no_records():
    with pytest.raises(ValueError): parse_fasta([])
def test_limit():
    with pytest.raises(ValueError): parse_fasta([">a","ATGC"], max_length=3)
def test_invalid_limit():
    with pytest.raises(ValueError): parse_fasta([">a","ATGC"], max_length=0)
