"""Initialize local SQLite database using the packaged idempotent migration."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from pulsemesh.settings import Settings  # noqa: E402
from pulsemesh.storage import EventStore  # noqa: E402

store = EventStore(Settings.from_env().database_path)
store.initialize()
print(f"Initialized {store.path}")
