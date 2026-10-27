# Scenario guide

- **Tariff arbitrage:** compare `price_aware` to `self_consumption` using the same deterministic trace. Price-aware charging from grid may increase imports while lowering energy cost; wear and peak charges can erase gains.
- **Solar curtailment:** set `grid_export_limit_kw=0` and use the baseline policy. Curtailed solar increases when generation exceeds demand.
- **Grid-constrained site:** lower `grid_import_limit_kw`; the simulator uses emergency battery discharge and then reports unserved energy.
- **Resilience:** create an outage using `--outage-start 100 --outage-length 12` and compare `resilience` to the other strategies. Reserve is consumed during an outage.
- **Battery efficiency:** change `roundtrip_efficiency` and compare losses, costs and SOC trajectory.

None of these scenarios represents an actual utility tariff or measured site without replacement of synthetic inputs.
