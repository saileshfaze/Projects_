"""Spectral indices and change masks."""
import numpy as np
from .models import Scene, Settings


def normalized_difference(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    den = a + b
    return np.divide(a - b, den, out=np.zeros_like(den, dtype=float), where=den > 1e-12)


def ndvi(scene: Scene) -> np.ndarray:
    return normalized_difference(scene.bands["nir"], scene.bands["red"])


def nbr(scene: Scene) -> np.ndarray:
    return normalized_difference(scene.bands["nir"], scene.bands["swir"])


def change_mask(before: Scene, after: Scene, settings: Settings) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    valid = ~(before.cloud | after.cloud)
    base_ndvi, next_ndvi = ndvi(before), ndvi(after)
    base_nbr, next_nbr = nbr(before), nbr(after)
    change = valid & (base_ndvi >= settings.min_baseline_ndvi)
    change &= (base_ndvi - next_ndvi >= settings.ndvi_drop)
    change &= (base_nbr - next_nbr >= settings.nbr_drop)
    return change, valid, base_ndvi - next_ndvi
