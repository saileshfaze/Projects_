import pytest

from atlasflow.fingerprints import sha256_records
from atlasflow.metrics import binary_metrics, population_stability_index


def test_binary_metrics_perfect():
    assert binary_metrics([1, 0, 1, 0], [1, 0, 1, 0]) == {
        "accuracy": 1.0, "precision": 1.0, "recall": 1.0, "f1": 1.0
    }


def test_binary_metrics_zero_division():
    result = binary_metrics([0, 0], [0, 0])
    assert result["f1"] == 0.0
    assert result["accuracy"] == 1.0


@pytest.mark.parametrize("actual,predicted", [([], []), ([1], []), ([2], [1])])
def test_invalid_binary_labels(actual, predicted):
    with pytest.raises(ValueError):
        binary_metrics(actual, predicted)


def test_psi_identical_and_shifted():
    reference = [float(i) for i in range(100)]
    assert population_stability_index(reference, reference) == pytest.approx(0)
    assert population_stability_index(reference, [x + 100 for x in reference]) > 1


def test_psi_rejects_nonfinite():
    with pytest.raises(ValueError):
        population_stability_index([1.0, float("nan")], [1.0])


def test_fingerprint_canonical_dict_order():
    assert sha256_records([{"a": 1, "b": 2}]) == sha256_records([{"b": 2, "a": 1}])
