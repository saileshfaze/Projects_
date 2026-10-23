# Evaluation protocol

The checked-in fictional dataset includes direct questions, one typo query, an abbreviated query, and an unanswerable query. Relevance judgments are manually specified in the generator and must not be interpreted as a validated benchmark.

- **Recall@k:** relevant documents retrieved / relevant documents labeled.
- **Precision@k:** relevant documents retrieved / k, including when fewer than k are returned.
- **MRR@k:** reciprocal rank of the first relevant result, or zero.
- **nDCG@k:** binary discounted gain divided by ideal gain.
- **95% bootstrap intervals:** deterministic percentile bootstrap over queries (500 resamples, seed 42). On this small corpus, intervals are unstable and do not justify statistical claims.

A query with no relevant labels receives zero for all metrics; evaluate abstention separately. The metrics measure retrieval **only**, not factual correctness or user satisfaction. Citation verification checks substring integrity but not truth. An extractive answer may still be misleading without broader context.

Run `python scripts/run_benchmark.py` to print the full JSON report. The project intentionally does not embed a performance claim in this document: report scores must be generated from the exact current code and dataset.
