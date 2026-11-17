"""Reproducible first-order RC thermal simulator; synthetic, not calibrated."""
from dataclasses import dataclass
from math import isfinite

@dataclass(frozen=True)
class Building:
    resistance_k_per_kw: float
    capacitance_kwh_per_k: float
    heating_capacity_kw: float
    cooling_capacity_kw: float
    initial_temp_c: float
    def __post_init__(self):
        vals=(self.resistance_k_per_kw,self.capacitance_kwh_per_k,self.heating_capacity_kw,self.cooling_capacity_kw,self.initial_temp_c)
        if not all(isfinite(x) for x in vals) or min(vals[:2])<=0 or min(vals[2:4])<0:
            raise ValueError('invalid building parameters')

@dataclass(frozen=True)
class Step:
    outdoor_c: float
    internal_kw: float = 0
    price_per_kwh: float = .2
    def __post_init__(self):
        if not all(isfinite(x) for x in (self.outdoor_c,self.internal_kw,self.price_per_kwh)) or self.price_per_kwh<0:
            raise ValueError('invalid weather, gain or tariff')

def simulate(building, weather, *, dt_hours=.25, target_c=21., deadband_c=.5, mode='thermostat'):
    if not isfinite(dt_hours) or dt_hours<=0 or dt_hours>building.resistance_k_per_kw*building.capacitance_kwh_per_k:
        raise ValueError('dt must be positive and <= RC time constant for explicit Euler stability')
    if not isfinite(target_c) or not isfinite(deadband_c) or deadband_c<0 or mode not in ('thermostat','off'):
        raise ValueError('invalid control settings')
    temperature=building.initial_temp_c; total_energy=total_cost=0.; records=[]
    for index,step in enumerate(weather):
        if not isinstance(step,Step):raise TypeError('weather entries must be Step')
        power=0.
        if mode=='thermostat':
            if temperature<target_c-deadband_c:power=building.heating_capacity_kw
            elif temperature>target_c+deadband_c:power=-building.cooling_capacity_kw
        conduction=(step.outdoor_c-temperature)/building.resistance_k_per_kw
        next_temp=temperature+dt_hours*(conduction+step.internal_kw+power)/building.capacitance_kwh_per_k
        energy=abs(power)*dt_hours;cost=energy*step.price_per_kwh
        total_energy+=energy;total_cost+=cost
        records.append({'step':index,'indoor_c':round(temperature,5),'next_c':round(next_temp,5),'outdoor_c':step.outdoor_c,'hvac_kw':power,'energy_kwh':round(energy,5),'cost':round(cost,5)})
        temperature=next_temp
    return {'steps':len(records),'final_temp_c':round(temperature,5),'energy_kwh':round(total_energy,5),'cost':round(total_cost,5),'trace':records}

def compare_controls(building,weather,**kwargs):
    weather=list(weather)
    on=simulate(building,weather,mode='thermostat',**kwargs)
    off=simulate(building,weather,mode='off',**kwargs)
    return {'thermostat':on,'uncontrolled':off,'energy_difference_kwh':round(on['energy_kwh']-off['energy_kwh'],5)}
