"""Deterministic two-date synthetic multispectral dataset and truth mask."""
import json
from pathlib import Path
import numpy as np
from .io import write_scene
from .models import Scene


def make_pair(size: int = 96, seed: int = 7) -> tuple[Scene, Scene, np.ndarray]:
    if size < 24 or size > 2048:
        raise ValueError("size must be between 24 and 2048")
    rng = np.random.default_rng(seed)
    y, x = np.mgrid[:size, :size]
    variation = 0.035*np.sin(x/9) + 0.025*np.cos(y/11)
    red = np.clip(0.14 + variation + rng.normal(0, 0.008, (size, size)), 0.03, 0.9)
    nir = np.clip(0.65 + variation + rng.normal(0, 0.012, (size, size)), 0.03, 0.95)
    swir = np.clip(0.22 + variation + rng.normal(0, 0.008, (size, size)), 0.03, 0.95)
    before_bands = {"red": red, "nir": nir, "swir": swir}
    truth = np.zeros((size, size), dtype=bool)
    for ya, yb, xa, xb in ((size//6, size//3, size//8, size//3),
                            (size//2, size*3//4, size//2, size*5//6),
                            (size//4, size//3, size*3//5, size*4//5)):
        truth[ya:yb, xa:xb] = True
    after_bands = {name: array.copy() for name, array in before_bands.items()}
    after_bands["red"][truth] += 0.15
    after_bands["nir"][truth] -= 0.32
    after_bands["swir"][truth] += 0.26
    after_bands = {name: np.clip(array + rng.normal(0, 0.006, array.shape), 0, 1)
                   for name, array in after_bands.items()}
    cloud_before = np.zeros_like(truth)
    cloud_after = np.zeros_like(truth)
    cloud_before[:size//8, size//3:size//2] = True
    cloud_after[size//2:size*5//8, size//2:size*5//8] = True
    transform = (420000.0, 10.0, 0.0, 4510000.0, 0.0, -10.0)
    return (Scene("synthetic-before", "2026-05-01T10:00:00Z", before_bands, cloud_before, transform),
            Scene("synthetic-after", "2026-09-01T10:00:00Z", after_bands, cloud_after, transform), truth)


def generate(root: Path, dataset_id: str = "demo", size: int = 96, seed: int = 7) -> Path:
    from .io import ID
    if not ID.fullmatch(dataset_id):
        raise ValueError("invalid dataset ID")
    directory = Path(root) / dataset_id
    if directory.exists():
        raise FileExistsError(f"refusing to overwrite existing dataset: {directory}")
    directory.mkdir(parents=True)
    before, after, truth = make_pair(size, seed)
    write_scene(directory / "before.npz", before)
    write_scene(directory / "after.npz", after)
    np.save(directory / "truth.npy", truth)
    (directory / "manifest.json").write_text(json.dumps({
        "dataset_id": dataset_id, "seed": seed, "size": size, "pixel_size_m": 10,
        "crs": "EPSG:3857", "truth": "truth.npy", "synthetic": True,
        "purpose": "deterministic software demonstration; not remote-sensing validation"
    }, indent=2) + "\n", encoding="utf-8")
    return directory
