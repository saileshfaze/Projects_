"""Basic DNA sequence operations."""
from collections import Counter

ALPHABET = frozenset("ACGTN")
COMPLEMENT = str.maketrans("ACGTN", "TGCAN")


def normalize(sequence: str) -> str:
    value = "".join(sequence.split()).upper()
    if not value:
        raise ValueError("DNA sequence cannot be empty")
    if any(base not in ALPHABET for base in value):
        raise ValueError("DNA contains unsupported symbols")
    return value


def reverse_complement(sequence: str) -> str:
    return normalize(sequence).translate(COMPLEMENT)[::-1]


def gc_fraction(sequence: str) -> float:
    value = normalize(sequence)
    informative = sum(base != "N" for base in value)
    return sum(base in "GC" for base in value) / informative if informative else 0.0


def kmer_counts(sequence: str, k: int) -> dict[str, int]:
    value = normalize(sequence)
    if not 1 <= k <= 20:
        raise ValueError("k must be between 1 and 20")
    counts = Counter(value[i:i+k] for i in range(len(value)-k+1)
                     if "N" not in value[i:i+k])
    return dict(sorted(counts.items()))
