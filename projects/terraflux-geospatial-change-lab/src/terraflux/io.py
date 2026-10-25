"""Safe scene dataset registry and NPZ serialization."""
import json
import re
from pathlib import Path
import numpy as np
from .models import BANDS, Scene

ID = re.compile(r"^[a-z][a-z0-9_-]{1,63}$")


def safe_dataset(root: Path, dataset_id: str) -> Path:
    if not ID.fullmatch(dataset_id):
        raise ValueError("dataset ID must be a lowercase slug")
    target = root.resolve() / dataset_id
    if target.is_symlink() or not target.is_dir():
        raise FileNotFoundError(dataset_id)
    if target.resolve().parent != root.resolve():
        raise ValueError("dataset must be inside data root")
    return target


def write_scene(path: Path, scene: Scene) -> None:
    scene.validate()
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(path, **scene.bands, cloud=scene.cloud,
                        scene_id=np.array(scene.scene_id), acquired_at=np.array(scene.acquired_at),
                        transform=np.array(scene.transform), crs=np.array(scene.crs))


def read_scene(path: Path) -> Scene:
    with np.load(path, allow_pickle=False) as archive:
        if set(archive.files) != set(BANDS) | {"cloud", "scene_id", "acquired_at", "transform", "crs"}:
            raise ValueError("unexpected NPZ fields")
        scene = Scene(str(archive["scene_id"]), str(archive["acquired_at"]),
                      {name: archive[name] for name in BANDS}, archive["cloud"],
                      tuple(float(x) for x in archive["transform"]), str(archive["crs"]))
    scene.validate()
    return scene


def load_pair(root: Path, dataset_id: str) -> tuple[Scene, Scene]:
    path = safe_dataset(root, dataset_id)
    return read_scene(path / "before.npz"), read_scene(path / "after.npz")


def write_report(path: Path, report: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
