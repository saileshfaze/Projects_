from dataclasses import replace
import numpy as np
import pytest
from terraflux.models import Settings
from terraflux.pipeline import analyze


def test_invalid_reflectance(pair):
    before, _, _ = pair
    before.bands['red'][0,0] = 2
    with pytest.raises(ValueError, match='reflectance'):
        before.validate()


def test_misaligned_scenes_rejected(pair):
    before, after, _ = pair
    bad = replace(after, transform=(0,10,0,0,0,-10))
    with pytest.raises(ValueError, match='co-registered'):
        analyze(before, bad)


def test_wrong_crs_rejected(pair):
    before, _, _ = pair
    with pytest.raises(ValueError, match='EPSG'):
        replace(before, crs='EPSG:4326').validate()


def test_reverse_time_rejected(pair):
    before, after, _ = pair
    with pytest.raises(ValueError, match='precede'):
        analyze(after, before)


def test_bad_settings_rejected():
    with pytest.raises(ValueError):
        Settings(min_patch_pixels=0).validate()
