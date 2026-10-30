# Explicit limitations and validity domain

- **Not for aviation operations:** This is a synthetic analytical laboratory, not certified
  conflict-detection or resolution software. Do not use for flight safety decisions.
- **Local tangent-plane approximation:** Equirectangular coordinates at a shared reference
  latitude are adequate only for short regional synthetic tracks; not for global or polar routes.
- **Linear segments:** No acceleration, wind, turn-rate, aircraft performance envelope,
  altitude pressure corrections, geodesic curves, or real trajectory prediction.
- **Separation thresholds:** 5 NM and 1,000 ft are demonstration defaults, not an assertion
  of universal regulatory minima. Real separation rules vary by context.
- **Uncertainty:** Gaussian *constant offsets per flight* represent one simplified error
  model, not validated navigation or surveillance uncertainty. Pair frequencies are
  Monte Carlo frequencies, not calibrated operational probabilities.
- **Advisories:** Delay offsets are scenario-level comparisons, not feasible or authorized
  maneuvers. A reduced conflict count is not proof of safety.
- **Persistence:** Hash chains detect naive data edits but do not prevent a privileged
  attacker from rewriting the database and recomputing all hashes. External anchoring
  and authenticated access would be needed for stronger assurances.
- **API:** Intended for local development only; no authentication, quotas, or production
  monitoring. Do not expose publicly without a gateway and operational safeguards.
