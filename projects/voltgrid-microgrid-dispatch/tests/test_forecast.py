import pytest
from voltgrid.forecast import seasonal_forecast

def test_seasonal_naive():
    result = seasonal_forecast([1.0, 2.0] * 24, horizon=3, season_length=2)
    assert result["point"] == [1.0, 2.0, 1.0]
    assert result["empirical_band_radius"] == 0

def test_requires_two_seasons():
    with pytest.raises(ValueError):
        seasonal_forecast([1.0, 2.0], horizon=1, season_length=2)

def test_nan_is_rejected():
    with pytest.raises(ValueError):
        seasonal_forecast([1.0, float("nan")] * 2, horizon=1, season_length=2)
