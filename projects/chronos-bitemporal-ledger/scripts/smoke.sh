#!/usr/bin/env sh
set -eu
python -m pytest -q
python scripts/generate_dataset.py --output /tmp/chronos-smoke.jsonl --tenants 1 --entities 3 --revisions 2
CHRONOS_DB=/tmp/chronos-smoke.sqlite3 python scripts/load_dataset.py --input /tmp/chronos-smoke.jsonl
