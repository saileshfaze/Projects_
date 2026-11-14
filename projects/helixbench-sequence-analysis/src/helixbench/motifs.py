"""Overlapping exact motif occurrences, with reference coordinates."""
from .sequence import normalize, reverse_complement


def find_motifs(sequence: str, motif: str, both_strands: bool = True) -> list[dict]:
    dna = normalize(sequence)
    target = normalize(motif)
    if len(target) > len(dna):
        return []
    results = []
    strands = [("+", dna)]
    if both_strands:
        strands.append(("-", reverse_complement(dna)))
    for strand, strand_dna in strands:
        for index in range(len(dna) - len(target) + 1):
            if strand_dna[index:index + len(target)] == target:
                start = index if strand == "+" else len(dna) - index - len(target)
                results.append({"start": start, "end": start + len(target), "strand": strand})
    return sorted(results, key=lambda row: (row["start"], row["strand"]))
