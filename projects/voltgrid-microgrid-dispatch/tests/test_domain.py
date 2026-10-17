import pytest
from pydantic import ValidationError
from voltgrid.domain import Scenario

def test_time_gap_rejected(scenario):
    payload = scenario.model_dump(mode="json")
    payload["slots"][2]["timestamp"] = payload["slots"][1]["timestamp"]
    with pytest.raises(ValidationError):
        Scenario.model_validate(payload)

def test_naive_timestamp_rejected(scenario):
    payload = scenario.model_dump(mode="json")
    payload["slots"][0]["timestamp"] = "2026-10-01T00:00:00"
    with pytest.raises(ValidationError):
        Scenario.model_validate(payload)

def test_tariff_arbitrage_rejected(scenario):
    payload = scenario.model_dump(mode="json")
    payload["slots"][0]["export_price_usd_per_kwh"] = 10
    with pytest.raises(ValidationError):
        Scenario.model_validate(payload)

def test_soc_bounds_rejected(scenario):
    payload = scenario.model_dump(mode="json")
    payload["battery"]["initial_soc_kwh"] = 99
    with pytest.raises(ValidationError):
        Scenario.model_validate(payload)
