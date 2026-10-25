import json
import numpy as np
import pytest
from terraflux.io import load_pair, safe_dataset, write_scene, read_scene
from terraflux.synthetic import generate


def test_scene_round_trip(tmp_path, pair):
    before, _, _ = pair
    path = tmp_path / 'scene.npz'
    write_scene(path, before)
    recovered = read_scene(path)
    assert recovered.scene_id == before.scene_id
    assert np.array_equal(recovered.bands['nir'], before.bands['nir'])


def test_generate_and_load(tmp_path):
    generate(tmp_path, 'demo', size=32)
    before, after = load_pair(tmp_path, 'demo')
    assert before.cloud.shape == after.cloud.shape == (32,32)
    with pytest.raises(FileExistsError):
        generate(tmp_path, 'demo', size=32)


def test_path_traversal_rejected(tmp_path):
    with pytest.raises(ValueError):
        safe_dataset(tmp_path, '../secret')


def test_symlink_rejected(tmp_path):
    (tmp_path / 'outside').mkdir()
    (tmp_path / 'link').symlink_to(tmp_path / 'outside')
    with pytest.raises(FileNotFoundError):
        safe_dataset(tmp_path, 'link')
