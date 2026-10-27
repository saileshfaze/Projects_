"""Validated domain models; kW values are interval-average power."""
from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import datetime
from math import isfinite


def _finite_nonnegative(value: float, label: str) -> None:
    if not isfinite(value) or value < 0:
        raise ValueError(f"{label} must be finite and nonnegative")


@dataclass(frozen=True)
class Battery:
    capacity_kwh: float = 20.0
    initial_soc_kwh: float = 10.0
    min_soc_kwh: float = 2.0
    max_soc_kwh: float = 20.0
    charge_kw: float = 7.0
    discharge_kw: float = 7.0
    roundtrip_efficiency: float = 0.90
    degradation_eur_per_kwh: float = 0.015

    def __post_init__(self) -> None:
        for key, value in asdict(self).items():
            _finite_nonnegative(value, key)
        if not 0 < self.capacity_kwh:
            raise ValueError("capacity must be positive")
        if not (0 <= self.min_soc_kwh <= self.initial_soc_kwh <= self.max_soc_kwh <= self.capacity_kwh):
            raise ValueError("invalid SOC bounds")
        if not (0 < self.roundtrip_efficiency <= 1):
            raise ValueError("roundtrip efficiency must be in (0,1]")


@dataclass(frozen=True)
class Site:
    battery: Battery = Battery()
    grid_import_limit_kw: float = 25.0
    grid_export_limit_kw: float = 15.0
    demand_charge_eur_per_kw: float = 0.0
    critical_load_fraction: float = 0.4
    resilience_reserve_fraction: float = 0.25

    def __post_init__(self) -> None:
        for name in ("grid_import_limit_kw", "grid_export_limit_kw", "demand_charge_eur_per_kw"):
            _finite_nonnegative(getattr(self, name), name)
        if not 0 <= self.critical_load_fraction <= 1:
            raise ValueError("critical_load_fraction must be in [0,1]")
        if not 0 <= self.resilience_reserve_fraction <= 1:
            raise ValueError("resilience_reserve_fraction must be in [0,1]")


@dataclass(frozen=True)
class Interval:
    timestamp: str
    load_kw: float
    pv_kw: float
    import_eur_per_kwh: float
    export_eur_per_kwh: float
    carbon_kg_per_kwh: float
    grid_available: bool = True

    def __post_init__(self) -> None:
        try:
            dt = datetime.fromisoformat(self.timestamp)
            if dt.tzinfo is None or dt.utcoffset() is None:
                raise ValueError("timestamp must include timezone")
        except (TypeError, ValueError) as exc:
            raise ValueError("timestamp must be ISO-8601 with timezone") from exc
        for name in ("load_kw", "pv_kw", "import_eur_per_kwh", "export_eur_per_kwh", "carbon_kg_per_kwh"):
            _finite_nonnegative(getattr(self, name), name)
        if not isinstance(self.grid_available, bool):
            raise ValueError("grid_available must be boolean")


@dataclass(frozen=True)
class Dispatch:
    timestamp: str
    soc_kwh: float
    grid_import_kwh: float
    grid_export_kwh: float
    battery_charge_kwh: float
    battery_discharge_kwh: float
    pv_curtailed_kwh: float
    load_shed_kwh: float
    critical_shed_kwh: float
    operating_cost_eur: float
    emissions_kg: float
    grid_available: bool


@dataclass(frozen=True)
class Summary:
    strategy: str
    intervals: int
    total_import_kwh: float
    total_export_kwh: float
    total_charge_kwh: float
    total_discharge_kwh: float
    curtailed_kwh: float
    unserved_kwh: float
    critical_unserved_kwh: float
    emissions_kg: float
    energy_cost_eur: float
    demand_charge_eur: float
    total_cost_eur: float
    peak_import_kw: float
    final_soc_kwh: float
