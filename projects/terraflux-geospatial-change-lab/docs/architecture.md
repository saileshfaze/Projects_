# Architecture and responsibilities

TerraFlux is a compact modular monolith. No task queue, cloud dependency, or remote imagery access is required.

1. **Dataset contract:** `Scene.validate()` checks reflectance bounds, mask types, timestamps, CRS, transform and band shapes. `load_pair()` reads a closed set of NPZ keys with pickle disabled.
2. **Spectral screening:** compute NDVI `(NIR-red)/(NIR+red)` and NBR `(NIR-SWIR)/(NIR+SWIR)`. Denominator zero yields zero. Candidates require sufficient baseline NDVI and both drop thresholds, excluding cloud pixels from either date.
3. **Spatial extraction:** eight-connected components group candidates; a minimum-pixel filter removes tiny patches. Pixel runs are converted to MultiPolygon cells without area inflation.
4. **Uncertainty:** draw bootstrap samples from nonoverlapping spatial blocks; compute changed/valid pixel ratios and report percentile bounds.
5. **Persistence:** canonical JSON + dataset slug is hashed to a stable run ID. SQLite `INSERT OR IGNORE` gives idempotent replays. This is not a tamper-evident audit log.
6. **API:** FastAPI accepts dataset IDs, not file paths; `/analyze` executes synchronously and stores reports. Use a process manager and request limits for a real deployment.

All modules can run independently in unit tests. The CLI uses the same library as the API.
