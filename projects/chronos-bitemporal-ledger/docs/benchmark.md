# Local benchmark methodology

The benchmark utility generates deterministic corrections, writes them to a fresh SQLite file and times ingestion with `time.perf_counter`. It reports throughput and a final audit result. Results depend on disk, filesystem, CPU, SQLite settings and concurrency; do not compare raw numbers across machines without controlling those factors.

```bash
python scripts/benchmark.py --events 1000 --db /tmp/chronos-bench.sqlite3
```

The script intentionally refuses to overwrite an existing database. It does not simulate concurrent production load, failures or multi-tenant access-control overhead.
