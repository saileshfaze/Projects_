"""Offline batch ingestion with deterministic ordering and failure isolation."""
from pathlib import Path
from .catalog import Catalog


def ingest_directory(catalog: Catalog, directory: str | Path) -> dict:
    folder = Path(directory)
    if not folder.is_dir():
        raise ValueError("directory does not exist")
    added, duplicate, errors = 0, 0, []
    for path in sorted(folder.glob("*.wav")):
        try:
            result = catalog.ingest(path.name, path.read_bytes())
            if result["deduplicated"]:
                duplicate += 1
            else:
                added += 1
        except (OSError, ValueError) as exc:
            errors.append({"file": path.name, "error": str(exc)})
    return {"added": added, "duplicates": duplicate, "errors": errors}
