import pytest
from helixbench.orfs import find_orfs

def test_forward(): assert { (x["start"],x["end"]) for x in find_orfs("ATGAAATAG") if x["strand"] == "+"} == {(0,9)}
def test_reverse(): assert any(x["strand"] == "-" for x in find_orfs("CTATTTCAT"))
def test_no_stop(): assert find_orfs("ATGAAA") == []
def test_no_start(): assert find_orfs("AAATAG") == []
def test_min_codons(): assert find_orfs("ATGTAA",3) == []
def test_two_codons(): assert len(find_orfs("ATGTAA")) == 1
def test_multiple_starts(): assert len(find_orfs("ATGATGTAA")) == 2
def test_stop_resets(): assert len(find_orfs("ATGTAAATGTAG")) == 2
def test_invalid_min():
    with pytest.raises(ValueError): find_orfs("ATGTAA",1)
