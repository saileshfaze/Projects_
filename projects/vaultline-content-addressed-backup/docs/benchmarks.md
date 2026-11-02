# Synthetic benchmark methodology

`scripts/benchmark.py` generates 40 fictional CSV files, snapshots the same
corpus twice, then reports logical bytes across snapshots and physical object
bytes. The logical-to-physical ratio illustrates content deduplication but is
not a measure of throughput, compression, disaster-recovery readiness, or
production storage cost. The corpus deliberately contains repeated prefixes.

No claims are made about real-world backup performance. Run on your own test
data, with permissions and source consistency controls, before evaluation.
