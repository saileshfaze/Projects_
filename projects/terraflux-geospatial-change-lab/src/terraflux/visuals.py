"""Deterministic false-color quicklooks for generated scenes."""
from pathlib import Path
import numpy as np
from PIL import Image
from .models import Scene


def quicklook(scene: Scene, path: Path) -> None:
    scene.validate()
    rgb = np.stack([scene.bands["nir"], scene.bands["red"], scene.bands["swir"]], axis=-1)
    rgb = np.clip(rgb * 1.3, 0, 1)
    rgb[scene.cloud] = [0.92, 0.92, 0.92]
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray((rgb*255).astype(np.uint8), "RGB").resize(
        (rgb.shape[1]*4, rgb.shape[0]*4), resample=Image.Resampling.NEAREST).save(path)


def mask_preview(mask: np.ndarray, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray((mask.astype(np.uint8)*255), "L").resize(
        (mask.shape[1]*4, mask.shape[0]*4), resample=Image.Resampling.NEAREST).save(path)
