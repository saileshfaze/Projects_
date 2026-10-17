"""Reusable deterministic dispatch fixture."""
from datetime import datetime, timedelta, timezone
import pytest
from voltgrid.domain import Battery, Grid, Scenario, Slot

@pytest.fixture
def scenario():
    start = datetime(2026, 10, 1, tzinfo=timezone.utc)
    slots = [
        Slot(timestamp=start + timedelta(hours=i), load_kw=load, solar_kw=0,
             import_price_usd_per_kwh=price, export_price_usd_per_kwh=0.05,
             grid_kgco2_per_kwh=0.4)
        for i, (load, price) in enumerate(zip([4, 4, 8, 8], [0.1, 0.1, 0.5, 0.5]))
    ]
    return Scenario(
        name="four-hour-test", interval_minutes=60, slots=slots,
        battery=Battery(capacity_kwh=8, initial_soc_kwh=4, min_soc_kwh=0,
                        target_final_soc_kwh=4, max_charge_kw=4, max_discharge_kw=4,
                        charge_efficiency=1, discharge_efficiency=1,
                        degradation_usd_per_kwh=0.005),
        grid=Grid(max_import_kw=20, max_export_kw=10,
                  demand_charge_usd_per_kw=0,
                  carbon_price_usd_per_kg=0),
    )
