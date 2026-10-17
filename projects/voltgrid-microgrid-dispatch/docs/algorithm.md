# Mathematical model and assumptions

For each interval t (duration Δ hours), the model chooses charge c_t, discharge d_t, grid import i_t, grid export e_t, solar curtailment u_t, ending battery SOC s_t, and binary charge-mode z_t. A common nonnegative peak P bounds i_t. All power variables are kW; SOC is kWh.

**Power balance:** i_t − e_t − c_t + d_t − u_t = load_t − solar_t.

**Battery state:** s_t = s_(t−1) + Δ η_charge c_t − Δ d_t / η_discharge. Initial SOC is fixed. minSOC ≤ s_t ≤ capacity and s_last ≥ terminalReserve.

**Exclusive battery mode:** c_t ≤ maxCharge · z_t; d_t ≤ maxDischarge · (1 − z_t), z_t ∈ {0,1}.

**Grid:** 0 ≤ i_t ≤ maxImport, 0 ≤ e_t ≤ maxExport, i_t ≤ P; 0 ≤ u_t ≤ solar_t.

**Objective (USD):** Σ_t Δ [importPrice_t · i_t − exportPrice_t · e_t + wear · (c_t+d_t) + carbonPrice · intensity_t · i_t + 0.0001 · u_t] + demandCharge · P.

The tiny solar curtailment penalty resolves otherwise indifferent export/curtail choices. The no-storage baseline uses the same tariff and demand-charge accounting, but deliberately does not enforce the optimized import cap; the output flags violations. Negative savings are possible for forced battery reserve or restrictive grid caps.

**Important modeling limits:** Prices must be nonnegative and export price ≤ import price. Equal zero tariffs can leave simultaneous grid import/export degenerate; an additional grid-direction binary would remove this ambiguity. No battery thermal dynamics, cycle-depth-dependent degradation, stochastic forecasts, network power flow, ramp rates or interconnection protection are modeled. Time limits and optimality gaps are configurable. The solver returns only status=0 (proven optimal within configured tolerance); other statuses are surfaced as failures.
