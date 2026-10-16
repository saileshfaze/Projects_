"""SQLite connection lifecycle and idempotent schema setup."""

from contextlib import contextmanager
from importlib.resources import files
from pathlib import Path
import sqlite3

from .timeutils import now_utc


class Database:
    def __init__(self, path: str):
        self.path = path

    @contextmanager
    def connect(self):
        if self.path != ":memory:":
            Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.path, timeout=15, isolation_level=None)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys=ON")
        conn.execute("PRAGMA busy_timeout=15000")
        if self.path != ":memory:":
            conn.execute("PRAGMA journal_mode=WAL")
        try:
            yield conn
        finally:
            conn.close()

    def migrate(self):
        migration = files("aegis_feature_store.migrations").joinpath("001_init.sql").read_text()
        with self.connect() as conn:
            conn.executescript(migration)
            conn.execute(
                "INSERT OR IGNORE INTO schema_migrations(version, applied_at) VALUES(1, ?)",
                (now_utc(),),
            )
