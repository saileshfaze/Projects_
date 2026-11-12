# SchemaHarbor — Data Contract Evolution Lab

**Sailesh / [saileshfaze](https://github.com/saileshfaze)** · MIT · Portfolio reference implementation

An offline Python toolkit for **schema evolution**, **CSV data quality checks**, and **downstream dependency impact analysis**. No cloud services or customer data are needed. It provides deterministic JSON reports and CI-friendly exit codes.

## Quick start

```bash
python -m pip install -e '.[dev]'
pytest -q
python scripts/generate_synthetic.py --rows 100 --seed 2026
schemaharbor diff data/orders-v1.json data/orders-v2.json --fail-breaking
schemaharbor check data/orders-v1.json data/orders-synthetic.csv
schemaharbor impact data/lineage.json orders
python scripts/demo.py
```

The `diff --fail-breaking` command intentionally exits **2** for a breaking change. `check` exits **1** when any row is invalid. Both are useful for release gates. All records and dependency names in examples are fictional.

## Architecture

- `contracts.py`: strict typed contract model and loader
- `compatibility.py`: deterministic backward-compatibility rules and version-bump recommendation
- `validation.py`: typed row validation and aggregated findings
- `lineage.py`: cycle-checked dependency graph and transitive impact
- `cli.py`: reproducible JSON output and meaningful exit codes

See `docs/design.md`, `docs/limitations.md`, and `assets/architecture.svg`.

## Scope and limitations

This is **not** a complete JSON Schema, Avro, or Protobuf compatibility implementation. It uses a deliberately small field vocabulary; its compatibility direction assumes that a new consumer must accept previously valid records. It does not authenticate callers, query production registries, or validate privacy compliance. CSV numeric coercion is intentionally permissive and should be tailored to your data contracts. Tests and synthetic fixtures are local engineering checks, not third-party certification.
