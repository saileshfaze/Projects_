# Synthetic data

`sample_events.jsonl` contains fictional tenant/plan pricing changes. No real customer records, personally identifiable information or proprietary data are included. The dataset is generated deterministically using `scripts/generate_dataset.py` and is safe to regenerate.

```bash
python scripts/generate_dataset.py --seed 42 --tenants 1 --entities 3 --revisions 4 --output data/sample_events.jsonl
```

Each JSONL row contains `tenant`, `entity`, and a `correction` object with a valid-time interval, payload, actor and idempotency key.
