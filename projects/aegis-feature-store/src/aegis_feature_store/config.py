"""Environment configuration; no credentials are stored in source control."""

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    db_path: str = "data/aegis.db"
    api_key: str | None = None
    max_batch_size: int = 5000

    @classmethod
    def from_env(cls) -> "Settings":
        batch_size = int(os.getenv("AEGIS_MAX_BATCH_SIZE", "5000"))
        if batch_size < 1:
            raise ValueError("AEGIS_MAX_BATCH_SIZE must be positive")
        return cls(
            db_path=os.getenv("AEGIS_DB_PATH", "data/aegis.db"),
            api_key=os.getenv("AEGIS_API_KEY") or None,
            max_batch_size=batch_size,
        )
