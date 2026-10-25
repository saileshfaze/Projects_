import numpy as np
from terraflux.spectral import normalized_difference, ndvi, nbr, change_mask
from terraflux.models import Settings


def test_zero_denominator_is_finite():
    result = normalized_difference(np.array([0.0, 1.0]), np.array([0.0, 1.0]))
    assert np.isfinite(result).all()
    assert result.tolist() == [0.0, 0.0]


def test_indices_are_bounded(pair):
    before, _, _ = pair
    assert np.abs(ndvi(before)).max() <= 1
    assert np.abs(nbr(before)).max() <= 1


def test_change_requires_both_indices(pair):
    before, after, truth = pair
    changed, valid, _ = change_mask(before, after, Settings())
    assert changed.sum() > 0
    assert np.all(~changed | valid)
    assert np.all(~changed | truth)


def test_clouds_are_excluded(pair):
    before, after, _ = pair
    changed, valid, _ = change_mask(before, after, Settings())
    assert not valid[before.cloud | after.cloud].any()
    assert not changed[before.cloud | after.cloud].any()
