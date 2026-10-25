"""Cloud-aware confusion metrics against a synthetic ground-truth mask."""
import numpy as np
from .geometry import components
from .models import Scene, Settings
from .spectral import change_mask


def evaluate(before: Scene, after: Scene, truth: np.ndarray,
             settings: Settings | None = None) -> dict:
    settings = settings or Settings()
    before.validate(); after.validate(); settings.validate()
    if truth.shape != before.cloud.shape or truth.dtype != np.dtype(bool):
        raise ValueError("truth must be a boolean mask with matching dimensions")
    candidates, valid, _ = change_mask(before, after, settings)
    predicted = np.zeros_like(valid)
    for group in components(candidates, settings.min_patch_pixels):
        for y, x in group:
            predicted[y, x] = True
    tp = int(np.sum(predicted & truth & valid))
    fp = int(np.sum(predicted & ~truth & valid))
    fn = int(np.sum(~predicted & truth & valid))
    precision = tp / (tp+fp) if tp+fp else 0.0
    recall = tp / (tp+fn) if tp+fn else 0.0
    return {"tp": tp, "fp": fp, "fn": fn,
            "precision": round(precision, 6), "recall": round(recall, 6),
            "f1": round(2*precision*recall/(precision+recall), 6) if precision+recall else 0.0,
            "iou": round(tp/(tp+fp+fn), 6) if tp+fp+fn else 0.0,
            "excluded_pixels": int((~valid).sum())}
