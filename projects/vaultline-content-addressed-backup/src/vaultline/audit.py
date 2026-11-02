"""Append-only hash-chained SQLite audit events (tamper-evident, not tamper-proof)."""
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from .chunking import sha256
from .manifest import canonical
from .errors import IntegrityError

class AuditLog:
    def __init__(self, db: Path):
        self.db = Path(db)
        self.db.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as c:
            c.execute("CREATE TABLE IF NOT EXISTS events (seq INTEGER PRIMARY KEY, at TEXT NOT NULL, action TEXT NOT NULL, payload TEXT NOT NULL, prev TEXT NOT NULL, digest TEXT NOT NULL)")

    def connect(self):
        return sqlite3.connect(self.db)

    def append(self, action: str, payload: dict):
        with self.connect() as c:
            last = c.execute("SELECT seq, digest FROM events ORDER BY seq DESC LIMIT 1").fetchone()
            seq, prev = (last[0] + 1, last[1]) if last else (1, "0" * 64)
            at = datetime.now(timezone.utc).isoformat()
            data = json.dumps(payload, sort_keys=True)
            digest = sha256(canonical(dict(seq=seq, at=at, action=action, payload=data, prev=prev)))
            c.execute("INSERT INTO events VALUES (?, ?, ?, ?, ?, ?)", (seq, at, action, data, prev, digest))
        return digest

    def verify(self):
        prev = "0" * 64
        count = 0
        with self.connect() as c:
            for seq, at, action, payload, link, digest in c.execute("SELECT * FROM events ORDER BY seq"):
                count += 1
                if seq != count or link != prev or sha256(canonical(dict(seq=seq, at=at, action=action, payload=payload, prev=link))) != digest:
                    raise IntegrityError(f"audit chain mismatch at event {seq}")
                prev = digest
        return count
