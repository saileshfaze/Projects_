import numpy as np
import pytest
from terraflux.evaluation import evaluate


def test_truth_evaluation(pair):
    before, after, truth = pair
    scores = evaluate(before, after, truth)
    assert scores['precision'] >= 0.99
    assert scores['recall'] > 0.65
    assert scores['f1'] > 0.75


def test_truth_shape_checked(pair):
    before, after, _ = pair
    with pytest.raises(ValueError):
        evaluate(before, after, np.zeros((2,2), dtype=bool))
