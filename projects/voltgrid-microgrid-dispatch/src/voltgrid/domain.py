"""Physical and tariff constraints, validated before optimization."""

from datetime import datetime, timedelta, timezone
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator

class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

class Slot(StrictModel):
    timestamp: datetime
    load_kw: float = Field(ge=0, allow_inf_nan=False)
    solar_kw: float = Field(ge=0, allow_inf_nan=False)
    import_price_usd_per_kwh: float = Field(ge=0, allow_inf_nan=False)
    export_price_usd_per_kwh: float = Field(ge=0, allow_inf_nan=False)
    grid_kgco2_per_kwh: float = Field(ge=0, allow_inf_nan=False)

    @model_validator(mode="after")
    def check_tariff(self):
        if self.timestamp.tzinfo is None or self.timestamp.utcoffset() is None:
            raise ValueError("timestamp must include a timezone")
        if self.export_price_usd_per_kwh > self.import_price_usd_per_kwh:
            raise ValueError("export price cannot exceed import price")
        return self

class Battery(StrictModel):
    capacity_kwh: float = Field(gt=0, allow_inf_nan=False)
    initial_soc_kwh: float = Field(ge=0, allow_inf_nan=False)
    min_soc_kwh: float = Field(ge=0, allow_inf_nan=False)
    target_final_soc_kwh: float = Field(ge=0, allow_inf_nan=False)
    max_charge_kw: float = Field(ge=0, allow_inf_nan=False)
    max_discharge_kw: float = Field(ge=0, allow_inf_nan=False)
    charge_efficiency: float = Field(gt=0, le=1, allow_inf_nan=False)
    discharge_efficiency: float = Field(gt=0, le=1, allow_inf_nan=False)
    degradation_usd_per_kwh: float = Field(ge=0, allow_inf_nan=False)

    @model_validator(mode="after")
    def check_soc(self):
        if not (self.min_soc_kwh <= self.initial_soc_kwh <= self.capacity_kwh
                and self.min_soc_kwh <= self.target_final_soc_kwh <= self.capacity_kwh):
            raise ValueError("SOC values must be within battery bounds")
        return self

class Grid(StrictModel):
    max_import_kw: float = Field(gt=0, allow_inf_nan=False)
    max_export_kw: float = Field(ge=0, allow_inf_nan=False)
    demand_charge_usd_per_kw: float = Field(ge=0, allow_inf_nan=False)
    carbon_price_usd_per_kg: float = Field(ge=0, allow_inf_nan=False)

class Scenario(StrictModel):
    name: str = Field(min_length=1, max_length=100)
    currency: Literal["USD"] = "USD"
    interval_minutes: Literal[15, 30, 60]
    slots: list[Slot] = Field(min_length=2, max_length=168)
    battery: Battery
    grid: Grid

    @model_validator(mode="after")
    def check_timeline(self):
        step = timedelta(minutes=self.interval_minutes)
        times = [s.timestamp.astimezone(timezone.utc) for s in self.slots]
        if any(b - a != step for a, b in zip(times, times[1:])):
            raise ValueError("timestamps must be strictly increasing with equal spacing")
        return self
