# ADR 0001: Frozen baseline

**Decision:** Calculate robust control limits from a designated baseline lot and never update the limits with production data during the same analysis. **Reason:** Re-estimating limits on shifted data can hide the very change under investigation. **Consequence:** Baseline management is manual; users must document process changes and approve new baselines.
