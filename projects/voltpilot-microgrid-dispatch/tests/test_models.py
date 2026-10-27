import pytest
from voltpilot.models import Battery, Site, Interval


@pytest.mark.parametrize("kwargs",[
    {"capacity_kwh":-1}, {"initial_soc_kwh":21}, {"min_soc_kwh":11},
    {"roundtrip_efficiency":0}, {"roundtrip_efficiency":1.1},
    {"charge_kw":float("nan")}, {"degradation_eur_per_kwh":-0.1}
])
def test_battery_rejects_invalid(kwargs):
    with pytest.raises(ValueError): Battery(**kwargs)


def test_site_rejects_invalid():
    with pytest.raises(ValueError): Site(critical_load_fraction=1.2)
    with pytest.raises(ValueError): Site(grid_import_limit_kw=-1)


def test_interval_requires_aware_timestamp():
    with pytest.raises(ValueError): Interval("2026-01-01T00:00:00",1,0,.2,.1,.2)


def test_interval_rejects_negative_power():
    with pytest.raises(ValueError): Interval("2026-01-01T00:00:00+00:00",-1,0,.2,.1,.2)
