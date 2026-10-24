# Statistical methodology and decision limits

## Unit of randomization

The experimental unit is a unique subject within an experiment. HMAC-SHA256 computes a uniform 64-bit fraction from experiment ID and subject ID under a salt. Fractions below `treatment_fraction` map to treatment B; the rest map to A. This is deterministic pseudorandom assignment, not a guarantee of balanced observed outcomes.

## Population and missingness

The assignment table counts everyone assigned. The outcome table contains at most one row per subject. A missing-outcome warning appears if >5% of assigned subjects have no recorded outcome; **missing not at random** can invalidate causal interpretations even when SRM passes. For a real experiment, collect explicit exposure events and predefine how unexposed or missing users are treated.

## Sample ratio mismatch

With observed assignments `A` and `B`, expected counts are `N(1-p)` and `Np`. Pearson's chi-square statistic is `Σ(observed-expected)^2/expected`. For exactly two arms the survival probability is `erfc(sqrt(chi_square/2))`. The alert threshold is p < 0.001, a diagnostic threshold, not a hypothesis-test correction.

## CUPED

The pooled coefficient is `θ = Cov(X,Y) / Var(X)`, where X is preperiod revenue and Y is observed revenue. The adjusted response is `Y* = Y - θ(X - mean(X))`. Centering is pooled across both arms. It can reduce variance if X predicts Y, but it is not guaranteed to help and may increase variance in small samples. No post-treatment covariates are permitted by the interface.

## Bootstrap and optional stopping

The report independently resamples each arm's observed outcomes 1,200 times and computes the distribution of the mean difference. The central percentile interval is descriptive; its nominal coverage may be poor with small, skewed or zero-inflated samples. A fixed seed enables reproducibility. `alpha_per_look = alpha / planned_looks` is a simple alpha-budget display, **not a complete sequential inference procedure**. Pre-register primary outcome, sample size, randomization unit, stopping plan, guardrails, and multiplicity adjustments before making decisions. Do not treat intervals as a deployment gate.

## Refund guardrail

Refund fraction is reported as a descriptive risk metric. Because refund events may arrive late, real systems should enforce a maturation window and record event-time corrections. Current storage allows one finalized row per subject; it does not model censoring or late revisions.
