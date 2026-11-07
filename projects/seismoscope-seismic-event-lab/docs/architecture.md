# Architecture and design choices

The core has zero runtime dependencies. `models` validates immutable station/pick records. `signal` uses prefix sums for O(n) STA/LTA energy ratios; detection applies hysteresis and cooldown. `associate` groups temporally adjacent station picks, requiring at least three distinct stations. `locate` evaluates each grid point using constant-velocity Euclidean travel times and least-squares origin-time residual. Deterministic seeds make regression tests reproducible. `api` is an optional, stateless adapter.

Complexity: detection O(SN) across S stations and N samples; grid search O(GP) for G grid points and P picks. A hard cap prevents runaway grid allocations. There is no persistence of real waveforms.
