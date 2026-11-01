"""Transactional SQLite audio catalog with idempotent ingestion and fingerprint search."""
from __future__ import annotations
from functools import wraps
from threading import RLock
from pathlib import Path
import hashlib
import json
import sqlite3
from .waveio import decode_wav
from .dsp import extract_features
from .fingerprint import fingerprints, Landmark, match_offsets

def synchronized(fn):
    @wraps(fn)
    def wrapper(self, *args, **kwargs):
        with self._lock:
            return fn(self, *args, **kwargs)
    return wrapper

SCHEMA = """
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS clips (
 id TEXT PRIMARY KEY, name TEXT NOT NULL, sha256 TEXT NOT NULL UNIQUE,
 duration_s REAL NOT NULL, sample_rate INTEGER NOT NULL, features_json TEXT NOT NULL,
 created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);
CREATE TABLE IF NOT EXISTS landmarks (
 clip_id TEXT NOT NULL REFERENCES clips(id) ON DELETE CASCADE,
 code TEXT NOT NULL, frame INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_landmark_code ON landmarks(code);
CREATE INDEX IF NOT EXISTS idx_landmark_clip ON landmarks(clip_id);
"""

class Catalog:
    def __init__(self, path: str | Path = ":memory:"):
        self._lock = RLock()
        self.conn = sqlite3.connect(str(path), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(SCHEMA)

    @synchronized
    def close(self) -> None:
        self.conn.close()

    @synchronized
    def ingest(self, name: str, raw: bytes) -> dict:
        if not name or len(name) > 120:
            raise ValueError("invalid clip name")
        audio = decode_wav(raw)
        if len(audio.samples) == 0:
            raise ValueError("empty clip")
        digest = hashlib.sha256(raw).hexdigest()
        clip_id = digest[:24]
        existing = self.conn.execute("SELECT * FROM clips WHERE sha256=?", (digest,)).fetchone()
        if existing:
            return self._row(existing) | {"deduplicated": True}
        features = extract_features(audio).to_dict()
        landmarks = fingerprints(audio)
        with self.conn:
            self.conn.execute("INSERT INTO clips(id,name,sha256,duration_s,sample_rate,features_json) VALUES(?,?,?,?,?,?)",
                              (clip_id, name, digest, audio.duration, audio.sample_rate, json.dumps(features, sort_keys=True)))
            self.conn.executemany("INSERT INTO landmarks(clip_id,code,frame) VALUES(?,?,?)",
                                  [(clip_id, x.code, x.frame) for x in landmarks])
        return {"id": clip_id, "name": name, "sha256": digest, "duration_s": audio.duration,
                "sample_rate": audio.sample_rate, "features": features,
                "landmarks": len(landmarks), "deduplicated": False}

    def _row(self, row: sqlite3.Row) -> dict:
        count = self.conn.execute("SELECT COUNT(*) FROM landmarks WHERE clip_id=?", (row["id"],)).fetchone()[0]
        return {"id": row["id"], "name": row["name"], "sha256": row["sha256"],
                "duration_s": row["duration_s"], "sample_rate": row["sample_rate"],
                "features": json.loads(row["features_json"]), "landmarks": count}

    @synchronized
    def list_clips(self) -> list[dict]:
        return [self._row(r) for r in self.conn.execute("SELECT * FROM clips ORDER BY name,id")]

    @synchronized
    def get(self, clip_id: str) -> dict | None:
        row = self.conn.execute("SELECT * FROM clips WHERE id=?", (clip_id,)).fetchone()
        return self._row(row) if row else None

    @synchronized
    def delete(self, clip_id: str) -> bool:
        with self.conn:
            result = self.conn.execute("DELETE FROM clips WHERE id=?", (clip_id,))
        return result.rowcount > 0

    @synchronized
    def search(self, raw: bytes, limit: int = 5) -> list[dict]:
        if not 1 <= limit <= 50:
            raise ValueError("invalid search limit")
        query_audio = decode_wav(raw)
        query = fingerprints(query_audio)
        if not query:
            return []
        # Bound query volume and fetch only matching code rows.
        by_clip: dict[str, list[Landmark]] = {}
        codes = sorted({x.code for x in query})
        for start in range(0, len(codes), 250):
            batch = codes[start:start+250]
            placeholders = ",".join("?" for _ in batch)
            for row in self.conn.execute(f"SELECT clip_id,code,frame FROM landmarks WHERE code IN ({placeholders})", batch):
                by_clip.setdefault(row["clip_id"], []).append(Landmark(row["code"], row["frame"]))
        results = []
        for clip_id, refs in by_clip.items():
            alignment = match_offsets(query, refs)
            if alignment["aligned_votes"]:
                row = self.get(clip_id)
                results.append({"clip_id": clip_id, "name": row["name"], **alignment})
        return sorted(results, key=lambda x: (-x["aligned_votes"], -x["confidence"], x["clip_id"]))[:limit]
