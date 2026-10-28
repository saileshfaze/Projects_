# Statistical notes

## Baseline

The center is the sample median. Dispersion uses `1.4826 × MAD`; if MAD is zero, sample standard deviation is used. A fully constant baseline raises an error. The normal-theory 1.4826 scaling is not distribution-free despite the robust estimator.

## Shewhart and run rules

Individual readings use `(x - center) / sigma`. The implementation flags points beyond ±3σ, two of three beyond ±2σ on the same side, four of five beyond ±1σ on the same side, eight on the same side, and six strictly monotonic. Rule families are not statistically independent; false alarm rates increase when multiple rules are combined. No ARL calibration is claimed.

## EWMA and CUSUM

EWMA is `z[t] = λ x[t] + (1-λ) z[t-1]` initialized at the baseline center, with time-dependent sigma `σ sqrt(λ/(2-λ) (1-(1-λ)^(2t)))`. CUSUM accumulates standardized positive/negative deviations with reference value `k=0.5`, decision interval `h=5`, and resets after a signal. These are demonstration defaults, not calibrated operating characteristics.

## Capability

Cp and Cpk estimate within-sigma from mean moving range divided by 1.128; Pp and Ppk use overall sample standard deviation. At least 20 observations are required. Values are not valid as decision criteria without stable process behavior, representative sampling and normality checks. The capability code reports null on zero variance.

## Change-point and multivariate

The split finder minimizes within-segment SSE with a minimum segment length. It does not provide a significance test or multiple-testing correction. Multivariate scores use a regularized sample covariance and an empirical training 99th-percentile threshold. It is optimistic on the same training data; evaluate out of sample before using it operationally.
