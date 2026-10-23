# VerityRAG Evidence Lab

An offline, reproducible workbench for hybrid document retrieval, source-span citation verification, and ranking evaluation.

This project uses BM25, character-trigram TF-IDF cosine, reciprocal rank fusion, deterministic bootstrap evaluation, and an extractive answer baseline. It deliberately does not use a generative model: character grams are lexical, not semantic embeddings.

The full project includes a FastAPI service, CLI, SQLite storage, synthetic operational runbooks, 18 tests, Docker, CI template, and technical documentation. The source files will be uploaded to this folder; see the release archive if publication is incomplete.

MIT License — Copyright (c) 2026 Sailesh.
