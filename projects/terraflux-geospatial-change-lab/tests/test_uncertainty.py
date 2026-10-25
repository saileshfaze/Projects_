import numpy as np
from terraflux.uncertainty import block_bootstrap_fraction


def test_no_valid_pixels():
    mask = np.zeros((8,8), dtype=bool)
    assert block_bootstrap_fraction(mask, mask) == (0.0, 0.0)


def test_full_change_is_certain():
    mask = np.ones((8,8), dtype=bool)
    assert block_bootstrap_fraction(mask, mask) == (1.0, 1.0)


def test_seed_reproducibility():
    mask = np.eye(12, dtype=bool)
    valid = np.ones_like(mask)
    assert block_bootstrap_fraction(mask, valid, seed=9) == block_bootstrap_fraction(mask, valid, seed=9)
