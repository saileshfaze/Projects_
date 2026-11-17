# Architecture

SQLite documents contain canonical titles, bodies and token counts. The postings table stores one row per `(term, document)` with frequency and comma-separated token positions. Replacements delete and reinsert within a single transaction; foreign keys cascade on delete. Search computes smoothed BM25 inverse document frequency, document-length normalization and a stable score/ID sort. Phrase matching checks contiguous positions in every term's postings list. All queries are parameterized.

Complexity: indexing a document is linear in its token count plus SQLite B-tree overhead. A query traverses postings for its unique terms, then scores candidates. No full-text extension is required.
