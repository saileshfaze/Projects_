import pytest

from aegis_feature_store.quality import drift_report, ks_statistic, psi


def test_identical_distributions_have_no_drift():
    values = [float(i) for i in range(100)]
    assert psi(values, values) == 0
    assert ks_statistic(values, values) == 0


def test_shift_detected():
    report = drift_report([float(i) for i in range(100)],
                          [float(i + 1000) for i in range(100)])
    assert report["psi"] > 0.2
    assert report["ks_statistic"] == 1
    assert report["psi_signal"] == "investigate"


def test_constant_reference_shift():
    assert psi([1, 1, 1], [1, 1, 1]) == 0
    assert psi([1, 1, 1], [2, 2, 2]) >= 0.2


def test_nonfinite_rejected():
    with pytest.raises(ValueError):
        psi([1, float("nan")], [1, 2])


def test_unequal_sizes_supported():
    assert 0 <= ks_statistic([1, 2, 3], [1, 2]) <= 1
