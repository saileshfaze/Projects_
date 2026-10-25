# Validation protocol

The automated suite covers: spectral edge cases, cloud masks, eight-connected components, pixel-accurate area, invalid reflectance, CRS and affine alignment, reverse chronology, deterministic output, high-threshold suppression, spatial bootstrap, safe dataset resolution, NPZ round trips, synthetic truth scoring, idempotent SQLite persistence, API endpoints, and CLI generation/evaluation.

Run `PYTHONPATH=src pytest -q` from the project root. The synthetic truth is constructed by the generator and must not be interpreted as independent external validation. For actual remote-sensing use, use separate georeferenced annotations and report class-specific confusion matrices with spatially separated validation areas.
