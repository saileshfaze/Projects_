"""Read-only dataset registry with explicit analysis and persisted reports."""
import os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from .io import load_pair, safe_dataset
from .models import Settings
from .pipeline import analyze
from .store import ReportStore


class AnalyzeRequest(BaseModel):
    dataset_id: str = Field(pattern=r"^[a-z][a-z0-9_-]{1,63}$")
    ndvi_drop: float = Field(default=0.20, gt=0, le=1)
    nbr_drop: float = Field(default=0.15, gt=0, le=1)
    min_patch_pixels: int = Field(default=6, ge=1, le=100000)


def create_app(data_root: Path | None = None, db_path: Path | None = None) -> FastAPI:
    root = Path(data_root or os.getenv("TERRAFLUX_DATA_ROOT", "data/generated"))
    db = Path(db_path or os.getenv("TERRAFLUX_DB_PATH", "state/reports.sqlite3"))
    store = ReportStore(db)
    app = FastAPI(title="TerraFlux Geospatial Change Lab", version="0.1.0")

    @app.get("/health")
    def health():
        return {"status": "ok", "service": "terraflux"}

    @app.get("/datasets")
    def datasets():
        if not root.is_dir():
            return {"datasets": []}
        found = []
        for p in root.iterdir():
            try:
                safe_dataset(root, p.name)
            except (ValueError, FileNotFoundError):
                continue
            if (p / "before.npz").is_file() and (p / "after.npz").is_file():
                found.append(p.name)
        return {"datasets": sorted(found)}

    @app.post("/analyze")
    def run(req: AnalyzeRequest):
        try:
            before, after = load_pair(root, req.dataset_id)
            settings = Settings(ndvi_drop=req.ndvi_drop, nbr_drop=req.nbr_drop,
                                min_patch_pixels=req.min_patch_pixels)
            report = analyze(before, after, settings)
        except (ValueError, FileNotFoundError, OSError) as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        run_id = store.put(req.dataset_id, report)
        return {"run_id": run_id, "report": report}

    @app.get("/reports")
    def list_reports(limit: int = 25):
        return {"runs": store.list_runs(limit)}

    @app.get("/reports/{run_id}")
    def get_report(run_id: str):
        if len(run_id) != 24 or any(c not in "0123456789abcdef" for c in run_id):
            raise HTTPException(status_code=404, detail="not found")
        result = store.get(run_id)
        if result is None:
            raise HTTPException(status_code=404, detail="not found")
        return result

    return app


app = create_app()
