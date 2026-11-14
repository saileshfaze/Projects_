from helixbench.motifs import find_motifs

def test_forward(): assert {x["start"] for x in find_motifs("ATGATG", "ATG", False)} == {0,3}
def test_overlapping(): assert len(find_motifs("AAAA", "AA", False)) == 3
def test_reverse(): assert {x["start"] for x in find_motifs("CAT", "ATG")} == {0}
def test_reverse_strand(): assert find_motifs("CAT", "ATG")[0]["strand"] == "-"
def test_absent(): assert find_motifs("AAA", "CCC") == []
def test_too_long(): assert find_motifs("AT", "ATG") == []
def test_palindrome(): assert len(find_motifs("ATAT", "AT")) == 4
