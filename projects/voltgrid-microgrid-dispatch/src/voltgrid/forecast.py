"""Seasonal-naive load forecast with backtested empirical error bands."""

import math
from statistics import median

def seasonal_forecast(
    history: list[float], horizon: int, season_length: int = 24, coverage: float = 0.9
) -> dict:
    if season_length < 1 or horizon < 1 or horizon > 168:
        raise ValueError("invalid season length or horizon")
    if not 0 < coverage < 1:
        raise ValueError("coverage must be between 0 and 1")
    if len(history) < 2 * season_length:
        raise ValueError("at least two complete seasons are required")
    if any(type(x) not in (float, int) or not math.isfinite(x) or x < 0 for x in history):
        raise ValueError("history must be finite, numeric and nonnegative")
    residuals = sorted(
        abs(history[i] - history[i - season_length])
        for i in range(season_length, len(history))
    )
    radius = residuals[min(len(residuals) - 1, int(coverage * len(residuals)))]
    values = [
        float(history[len(history) - season_length + i % season_length])
        for i in range(horizon)
    ]
    return {
        "method": "seasonal_naive",
        "point": values,
        "lower": [max(0.0, x - radius) for x in values],
        "upper": [x + radius for x in values],
        "residual_median": median(residuals),
        "empirical_band_radius": radius,
    }
