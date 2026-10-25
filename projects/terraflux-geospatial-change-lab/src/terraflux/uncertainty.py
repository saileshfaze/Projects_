"""Spatial block bootstrap of the changed-pixel fraction."""
import numpy as np


def block_bootstrap_fraction(changed: np.ndarray, valid: np.ndarray, *,
                             block_size: int = 8, samples: int = 200,
                             seed: int = 42) -> tuple[float, float]:
    if changed.shape != valid.shape or changed.ndim != 2:
        raise ValueError("changed/valid shape mismatch")
    if not valid.any():
        return 0.0, 0.0
    h, w = changed.shape
    counts = []
    for y in range(0, h, block_size):
        for x in range(0, w, block_size):
            block = np.s_[y:y+block_size, x:x+block_size]
            counts.append((int(np.count_nonzero(changed[block] & valid[block])),
                           int(np.count_nonzero(valid[block]))))
    counts = np.asarray(counts, dtype=np.int64)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(counts), size=(samples, len(counts)))
    drawn = counts[idx].sum(axis=1)
    rates = np.divide(drawn[:, 0], drawn[:, 1],
                      out=np.zeros(samples, dtype=float), where=drawn[:, 1] > 0)
    lo, hi = np.quantile(rates, [0.025, 0.975])
    return round(float(lo), 6), round(float(hi), 6)
