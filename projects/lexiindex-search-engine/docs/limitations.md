# Scope and limitations

This is an educational retrieval engine, not a production search cluster. Tokenization is ASCII-oriented and deliberately does not support stemming, Unicode word segmentation, stop-word removal, field boosting, fuzzy matching, distributed indexing, access control or relevance evaluation. BM25 results are deterministic but not independently benchmarked against an established engine. Avoid indexing sensitive data; the database stores full text in plaintext.
