# LexiIndex — SQLite Search Engine Lab

**Sailesh / [saileshfaze](https://github.com/saileshfaze)** · MIT · Software engineering portfolio

An offline inverted-index retrieval system implemented without an external search service. Features include SQLite-backed postings with positional data, transactional document replacement, BM25 ranking, deterministic tie-breaking, exact phrase matching, CLI ingestion, and reproducible synthetic corpora.

## Quick start

```bash
python -m pip install -e . --no-build-isolation
python -m pytest -q
python -m lexiindex --db /tmp/lexiindex.db ingest data/sample.jsonl
python -m lexiindex --db /tmp/lexiindex.db search 'search term' --phrase
python scripts/generate.py --count 100 --seed 2026
```

See `docs/design.md` and `docs/limitations.md`. No personal data, customer usage or production benchmarks are included.
