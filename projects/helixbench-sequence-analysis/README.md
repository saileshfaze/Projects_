# HelixBench — Synthetic DNA Sequence Analysis Lab

Portfolio project by **Sailesh / saileshfaze**. A dependency-light, deterministic bioinformatics reference implementing FASTA parsing, GC content, reverse complements, k-mer spectra, exact motif search on both strands, and six-frame open reading frame (ORF) discovery. All included sequences are synthetic.

## Quick start

```bash
python -m pip install -e .
helixbench analyze --sequence ATGAAATAG --k 3
helixbench fasta data/synthetic.fasta --k 3
python scripts/generate_synthetic.py --output output/synthetic.fasta
python scripts/demo.py
python -m pytest -q
```

`helixbench analyze` emits deterministic JSON. `helixbench fasta` analyzes multiple records with a per-record limit. The optional API is available with `pip install -e '.[api]'` and `uvicorn helixbench.api:app`.

## Engineering choices

- Strict DNA alphabet A/C/G/T/N, normalized to uppercase; no IUPAC ambiguity expansion.
- Streaming FASTA record parsing with duplicate identifier rejection and bounded record length.
- Reverse-strand positions reported in reference-coordinate intervals, 0-based and half-open.
- ORFs require an in-frame ATG start and one of TAA/TAG/TGA stop codons; stop codon included in interval.
- K-mers containing N are excluded from counted spectrum; all counted windows overlap.
- No network requests, reference genomes, or patient/genomic personal data.

## Limitations

Educational, synthetic data only. No alignment, quality scores, gene annotation, splice variants, genetic-code variants, biological validation, or clinical use. The CLI is not designed for huge whole-genome inputs. See docs/design.md and docs/limitations.md.
