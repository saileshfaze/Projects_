"""Transactional SQLite document and evaluation storage."""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from .retrieval import Document

SCHEMA = """
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS documents (
 id TEXT PRIMARY KEY, title TEXT NOT NULL, body TEXT NOT NULL,
 source TEXT NOT NULL, category TEXT NOT NULL,
 content_hash TEXT NOT NULL, updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS evaluations (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
 corpus_hash TEXT NOT NULL, result_json TEXT NOT NULL
);
"""


def connect(path: str | Path) -> sqlite3.Connection:
    path = str(path)
    if path != ":memory:":
        Path(path).parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(path, timeout=15)
    con.row_factory = sqlite3.Row
    con.executescript(SCHEMA)
    return con


def ingest(con: sqlite3.Connection, documents: list[Document]) -> int:
    import hashlib
    if len({d.id for d in documents}) != len(documents):
        raise ValueError("duplicate IDs in batch")
    with con:
        for doc in documents:
            if not doc.id or not doc.title or not doc.body:
                raise ValueError("id, title and body required")
            digest = hashlib.sha256(doc.text.encode()).hexdigest()
            con.execute("""INSERT INTO documents(id,title,body,source,category,content_hash)
                VALUES(?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET
                title=excluded.title,body=excluded.body,source=excluded.source,
                category=excluded.category,content_hash=excluded.content_hash,
                updated_at=CURRENT_TIMESTAMP""",
                (doc.id, doc.title, doc.body, doc.source, doc.category, digest))
    return len(documents)


def all_documents(con: sqlite3.Connection) -> list[Document]:
    return [Document(r["id"], r["title"], r["body"], r["source"], r["category"])
            for r in con.execute("SELECT * FROM documents ORDER BY id")]


def corpus_hash(con: sqlite3.Connection) -> str:
    import hashlib
    data = "\n".join(f'{r[0]}:{r[1]}' for r in
                     con.execute("SELECT id,content_hash FROM documents ORDER BY id"))
    return hashlib.sha256(data.encode()).hexdigest()


def save_evaluation(con: sqlite3.Connection, result: dict) -> int:
    with con:
        cur = con.execute("INSERT INTO evaluations(corpus_hash,result_json) VALUES(?,?)",
                          (corpus_hash(con), json.dumps(result, sort_keys=True)))
    return int(cur.lastrowid)
