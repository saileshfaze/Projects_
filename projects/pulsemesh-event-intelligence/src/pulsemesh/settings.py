"""Environment-based configuration; never commit runtime secrets."""
from dataclasses import dataclass
from pathlib import Path
import os


@dataclass(frozen=True)
class Settings:
    database_path: Path = Path("./var/pulsemesh.sqlite3")
    api_key: str = ""
    allowed_lateness_seconds: int = 3600
    max_batch_size: int = 500

    @classmethod
    def from_env(cls) -> "Settings":
        lateness = int(os.getenv("PULSEMESH_ALLOWED_LATENESS_SECONDS", "3600"))
        batch = int(os.getenv("PULSEMESH_MAX_BATCH_SIZE", "500"))
        if lateness < 0 or not 1 <= batch <= 5000:
            raise ValueError("Invalid PULSEMESH lateness or batch size")
        return cls(
            database_path=Path(os.getenv("PULSEMESH_DATABASE_PATH", "./var/pulsemesh.sqlite3")),
            api_key=os.getenv("PULSEMESH_API_KEY", ""),
            allowed_lateness_seconds=lateness,
            max_batch_size=batch,
        )
