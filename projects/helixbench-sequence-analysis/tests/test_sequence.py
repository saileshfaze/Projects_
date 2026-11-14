import pytest
from helixbench.sequence import normalize, reverse_complement, gc_fraction, kmer_counts

def test_normalize(): assert normalize(" atg n ") == "ATGN"
def test_empty():
    with pytest.raises(ValueError): normalize(" ")
def test_invalid():
    with pytest.raises(ValueError): normalize("ATX")
def test_reverse(): assert reverse_complement("ATGCN") == "NGCAT"
def test_reverse_involution(): assert reverse_complement(reverse_complement("ATGCNN")) == "ATGCNN"
def test_gc(): assert gc_fraction("GGCANN") == .75
def test_gc_ambiguous(): assert gc_fraction("NN") == 0
def test_kmer_overlap(): assert kmer_counts("AAAA", 2) == {"AA": 3}
def test_kmer_n(): assert kmer_counts("AANAA", 2) == {"AA": 2}
def test_kmer_large(): assert kmer_counts("AC", 3) == {}
@pytest.mark.parametrize("k", [0, 21, -1])
def test_invalid_k(k):
    with pytest.raises(ValueError): kmer_counts("ACGT", k)
