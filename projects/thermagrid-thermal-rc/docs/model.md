# Model and architecture

State: indoor air/aggregate thermal mass temperature `T` in °C. For thermal resistance `R` (K/kW), thermal capacitance `C` (kWh/K), outdoor temperature `Tout`, internal gain `Qint` and signed HVAC power `Qhvac`, the state derivative is `dT/dt = ((Tout-T)/R + Qint + Qhvac)/C`. The explicit Euler update uses `T_next = T + dt*dT/dt`. `dt` is bounded by `R*C` to avoid a simple numerical stability failure; this does not guarantee accuracy. A deadband thermostat uses a discrete heating/cooling command based on current temperature. Energy is `abs(Qhvac)*dt`, not electrical input with a coefficient of performance. Costs are energy times tariff.

Pipeline: JSON scenario → dataclass validation → deterministic step loop → trace and totals → JSON report. No cloud services, secrets, or real sensors.
