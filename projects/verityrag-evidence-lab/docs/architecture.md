# Architecture and data flow

The service reads SQLite documents into an immutable in-memory `HybridIndex` for each request. This is simple and consistent for small corpora but costs O(N) preprocessing per request; a production design would cache versioned indexes and use a durable external index.

**BM25** uses term frequency, corpus document frequency, length normalization (`k1=1.5`, `b=0.75`). **Character TF-IDF** uses 3-grams, smoothed IDF, log TF and cosine similarity. Each ranked list excludes zero/near-zero evidence. **RRF** combines ranks as `sum(1/(60+rank))`; document ID breaks ties.

Answering scans sentence-like spans in ranked documents, rejects entire documents matching explicit instruction-attack patterns, ranks candidate spans by query-term overlap and retrieval score, and returns at most two source excerpts. Source offsets are validated before the API responds. Redaction changes display text but never the underlying offset indices.

Evaluation joins `questions.jsonl` and `qrels.jsonl` by stable query ID, reports per-query and per-slice scores, and stores the report with a corpus content hash. A hash detects corpus changes; it is not an authenticity signature.

The SQLite connection is kept in the FastAPI lifespan and used by async handlers on the event-loop thread. This intentionally avoids cross-thread SQLite use but **blocks the event loop** during database operations. It is appropriate only for small local demos, not high concurrency.
