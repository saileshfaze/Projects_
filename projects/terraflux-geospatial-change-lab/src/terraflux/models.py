"""Immutable scene contracts and analysis configuration."""
from dataclasses import dataclass
from datetime import datetime
import numpy as np

BANDS = ("red", "nir", "swir")


@dataclass(frozen=True)
class Scene:
    scene_id: str
    acquired_at: str
    bands: dict[str, np.ndarray]
    cloud: np.ndarray
    transform: tuple[float, float, float, float, float, float]
    crs: str = "EPSG:3857"

    def validate(self) -> None:
        if not self.scene_id or not self.acquired_at:
            raise ValueError("scene_id and acquired_at are required")
        try:
            datetime.fromisoformat(self.acquired_at.replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValueError("acquired_at must be ISO-8601") from exc
        if set(self.bands) != set(BANDS):
            raise ValueError(f"exactly {BANDS} bands are required")
        shape = self.cloud.shape
        if len(shape) != 2 or not all(x > 0 for x in shape):
            raise ValueError("cloud mask must be a nonempty 2D array")
        if self.cloud.dtype != np.dtype(bool):
            raise ValueError("cloud mask must be boolean")
        for name, array in self.bands.items():
            if array.shape != shape or not np.issubdtype(array.dtype, np.number):
                raise ValueError(f"{name} shape/type does not match cloud mask")
            if not np.isfinite(array).all() or np.any((array < 0) | (array > 1)):
                raise ValueError(f"{name} reflectance must be finite and in [0, 1]")
        if len(self.transform) != 6 or not all(np.isfinite(self.transform)):
            raise ValueError("invalid affine transform")
        a, b, c, d, e, f = self.transform
        if b <= 0 or f >= 0 or c != 0 or e != 0:
            raise ValueError("north-up, non-rotated affine transform required")
        if self.crs != "EPSG:3857":
            raise ValueError("this prototype accepts EPSG:3857 only")


@dataclass(frozen=True)
class Settings:
    ndvi_drop: float = 0.20
    nbr_drop: float = 0.15
    min_baseline_ndvi: float = 0.25
    min_patch_pixels: int = 6
    bootstrap_samples: int = 200
    block_size: int = 8
    seed: int = 42

    def validate(self) -> None:
        if not (0 < self.ndvi_drop <= 1 and 0 < self.nbr_drop <= 1):
            raise ValueError("drop thresholds must be in (0,1]")
        if not (-1 <= self.min_baseline_ndvi <= 1):
            raise ValueError("baseline NDVI outside [-1,1]")
        if self.min_patch_pixels < 1 or self.bootstrap_samples < 1 or self.block_size < 1:
            raise ValueError("positive patch, bootstrap, block settings required")
