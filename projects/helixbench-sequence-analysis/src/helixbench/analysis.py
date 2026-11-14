"""Assemble deterministic JSON-compatible sequence reports."""
from .sequence import normalize, reverse_complement, gc_fraction, kmer_counts
from .motifs import find_motifs
from .orfs import find_orfs


def analyze(sequence: str, k: int = 3, motif: str = "ATG", min_codons: int = 2) -> dict:
    dna = normalize(sequence)
    return {"length": len(dna), "gc_fraction": gc_fraction(dna),
            "ambiguous_bases": dna.count("N"), "reverse_complement": reverse_complement(dna),
            "kmers": kmer_counts(dna, k), "motif": motif.upper(),
            "motif_hits": find_motifs(dna, motif), "orfs": find_orfs(dna, min_codons)}
