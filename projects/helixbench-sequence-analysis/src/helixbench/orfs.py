"""Six-frame ATG-to-stop ORF scanner."""
from .sequence import normalize, reverse_complement
STOPS = {"TAA", "TAG", "TGA"}


def find_orfs(sequence: str, min_codons: int = 2) -> list[dict]:
    dna = normalize(sequence)
    if min_codons < 2:
        raise ValueError("min_codons must be >= 2")
    found = []
    for strand, seq in (("+", dna), ("-", reverse_complement(dna))):
        for frame in range(3):
            starts = []
            for i in range(frame, len(seq) - 2, 3):
                codon = seq[i:i + 3]
                if codon == "ATG":
                    starts.append(i)
                elif codon in STOPS:
                    for start in starts:
                        if (i + 3 - start) // 3 >= min_codons:
                            left = start if strand == "+" else len(dna) - i - 3
                            right = i + 3 if strand == "+" else len(dna) - start
                            found.append({"start": left, "end": right, "strand": strand,
                                          "frame": frame, "codons": (i + 3 - start) // 3})
                    starts = []
    return sorted(found, key=lambda item: (item["start"], item["end"], item["strand"]))
