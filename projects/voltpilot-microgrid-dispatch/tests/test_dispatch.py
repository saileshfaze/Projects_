from math import isclose
import pytest
from voltpilot.dispatch import simulate,compare,STRATEGIES
from voltpilot.models import Battery,Site
from voltpilot.synthetic import generate


@pytest.mark.parametrize("strategy",STRATEGIES)
def test_energy_accounting_and_soc(profile,site,strategy):
    summary,steps=simulate(profile,site,strategy)
    assert len(steps)==len(profile)
    assert summary.total_import_kwh>=0
    assert all(site.battery.min_soc_kwh-1e-8 <= x.soc_kwh <= site.battery.max_soc_kwh+1e-8 for x in steps)
    assert all(x.grid_import_kwh<=site.grid_import_limit_kw*.25+1e-8 for x in steps)
    assert all(x.grid_export_kwh<=site.grid_export_limit_kw*.25+1e-8 for x in steps)
    for row,x in zip(profile,steps):
        supply=(row.pv_kw*.25+x.grid_import_kwh+x.battery_discharge_kwh)
        demand=(row.load_kw*.25-x.load_shed_kwh+x.battery_charge_kwh+x.grid_export_kwh+x.pv_curtailed_kwh)
        assert isclose(supply,demand,abs_tol=1e-7)


def test_baseline_does_not_cycle_battery(profile,site):
    _,steps=simulate(profile,site,"baseline")
    assert all(x.battery_charge_kwh==0 and x.battery_discharge_kwh==0 for x in steps)


def test_outage_sheds_load_and_never_uses_grid(site):
    p=generate(days=1,outage_start=0,outage_length=16)
    summary,steps=simulate(p,site,"resilience")
    assert all(not x.grid_available and x.grid_import_kwh==0 and x.grid_export_kwh==0 for x in steps[:16])
    assert summary.unserved_kwh>0


def test_import_cap_fallback_to_battery(profile):
    site=Site(grid_import_limit_kw=0)
    _,steps=simulate(profile,site,"baseline")
    assert all(x.grid_import_kwh==0 for x in steps)
    assert sum(x.battery_discharge_kwh for x in steps)>0


def test_zero_export_limit_curtailed(profile):
    site=Site(grid_export_limit_kw=0)
    summary,steps=simulate(profile,site,"baseline")
    assert all(x.grid_export_kwh==0 for x in steps)
    assert summary.curtailed_kwh>0


def test_price_aware_grid_charge_occurs(profile,site):
    _,steps=simulate(profile,site,"price_aware")
    assert any(x.grid_import_kwh > row.load_kw*.25+1e-7 for x,row in zip(steps,profile) if row.pv_kw==0)


def test_resilience_maintains_reserve_when_grid_available(profile):
    site=Site(battery=Battery(initial_soc_kwh=15),resilience_reserve_fraction=.65)
    _,steps=simulate(profile,site,"resilience")
    assert all(x.soc_kwh>=site.battery.capacity_kwh*.65-1e-8 for x in steps)


def test_unknown_policy_rejected(profile,site):
    with pytest.raises(ValueError): simulate(profile,site,"unknown")


def test_discontinuous_times_rejected(profile,site):
    with pytest.raises(ValueError): simulate(profile[:5]+profile[6:],site)


def test_empty_profile_rejected(site):
    with pytest.raises(ValueError): simulate([],site)


def test_bad_cadence_rejected(profile,site):
    with pytest.raises(ValueError): simulate(profile,site,step_minutes=17)


def test_comparison_contains_all_strategies(profile,site):
    assert set(compare(profile,site))==set(STRATEGIES)


def test_reproducible_results(profile,site):
    assert simulate(profile,site)==simulate(profile,site)
