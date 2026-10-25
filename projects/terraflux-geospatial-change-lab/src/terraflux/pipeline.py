"""Reproducible geospatial screening pipeline."""
from dataclasses import asdict
import numpy as np
from .geometry import components, feature_collection
from .models import Scene, Settings
from .spectral import change_mask, ndvi, nbr
from .uncertainty import block_bootstrap_fraction


def analyze(before: Scene, after: Scene, settings: Settings | None = None) -> dict:
    settings = settings or Settings()
    before.validate()
    after.validate()
    settings.validate()
    if before.bands["red"].shape != after.bands["red"].shape:
        raise ValueError("scenes must share pixel dimensions")
    if before.transform != after.transform or before.crs != after.crs:
        raise ValueError("scenes must be co-registered and share a CRS")
    if before.acquired_at >= after.acquired_at:
        raise ValueError("before acquisition must precede after acquisition")
    candidates, valid, drops = change_mask(before, after, settings)
    groups = components(candidates, settings.min_patch_pixels)
    retained = np.zeros_like(valid, dtype=bool)
    for group in groups:
        for row, col in group:
            retained[row, col] = True
    total, changed = int(valid.sum()), int(retained.sum())
    pixel_area = abs(before.transform[1] * before.transform[5])
    lo, hi = block_bootstrap_fraction(retained, valid, block_size=settings.block_size,
                                      samples=settings.bootstrap_samples, seed=settings.seed)
    def valid_mean(arr: np.ndarray) -> float | None:
        return round(float(arr[valid].mean()), 5) if total else None
    return {"schema_version": 1, "before_scene": before.scene_id,
            "after_scene": after.scene_id, "acquired_before": before.acquired_at,
            "acquired_after": after.acquired_at, "settings": asdict(settings),
            "summary": {"total_pixels": int(valid.size), "valid_pixels": total,
                        "cloud_excluded_pixels": int(valid.size-total),
                        "changed_pixels": changed, "changed_area_m2": round(changed*pixel_area, 3),
                        "changed_fraction": round(changed/total, 6) if total else 0.0,
                        "block_bootstrap_95": [lo, hi], "patch_count": len(groups),
                        "mean_ndvi_before": valid_mean(ndvi(before)),
                        "mean_ndvi_after": valid_mean(ndvi(after)),
                        "mean_nbr_before": valid_mean(nbr(before)),
                        "mean_nbr_after": valid_mean(nbr(after))},
            "geojson": feature_collection(groups, before.transform, drops)}
