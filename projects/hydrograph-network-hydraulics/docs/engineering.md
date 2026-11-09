# Numerical method and limitations

Each edge uses a smoothed quadratic head-loss relation `q = Δh / sqrt(R * sqrt(Δh² + ε²))`, with positive flow from `start` to `end`. The ε regularization makes the derivative finite at zero flow. Node continuity residual is incoming minus outgoing minus prescribed demand. A damped Newton method assembles the analytic Jacobian and solves `J Δh = -r` by partial-pivot Gaussian elimination. Backtracking accepts only strictly decreasing maximum absolute node residual. Convergence is defined by the specified continuity tolerance, not field accuracy.

This is a steady-state, single-reservoir, fixed-demand graph model. It is not a hydraulic design tool and cannot assess actual pressures, water quality or regulatory compliance. The Monte Carlo draws use seeded Gaussian multipliers, truncated at zero, and are not a calibrated demand forecast. A converged numerical result does not imply physical validity.

Scalability: dense O(N³) linear solves; no sparse Jacobian, trust-region globalization or graph partitioning. Underconstrained networks and difficult scenarios can fail to converge. Failure must be surfaced, not hidden. API is unauthenticated and intended for local testing only.
