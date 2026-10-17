"""Environment-based runtime configuration."""

import os
from dataclasses import dataclass

@dataclass(frozen=True)
class Settings:
    database_path: str = "data/voltgrid.sqlite3"
    solver_time_limit_seconds: float = 20.0
    solver_relative_gap: float = 0.001

    @classmethod
    def from_env(cls):
        return cls(
            database_path=os.getenv("VOLTGRID_DB_PATH", "data/voltgrid.sqlite3"),
            solver_time_limit_seconds=float(os.getenv("VOLTGRID_SOLVER_TIMEOUT", "20")),
            solver_relative_gap=float(os.getenv("VOLTGRID_SOLVER_GAP", "0.001")),
        )
