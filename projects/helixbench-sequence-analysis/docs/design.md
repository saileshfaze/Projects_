# Architecture

`fasta` parses records; `sequence` handles alphabet, reverse complement and GC; `motifs` searches exact matches; `orfs` finds bounded start-to-stop codons in six frames; `analysis` assembles JSON-ready summaries; `cli` handles local input; `api` provides optional HTTP. All algorithms are deterministic, dependency-light and operate on synthetic examples.
