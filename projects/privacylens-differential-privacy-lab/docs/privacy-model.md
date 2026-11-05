# Privacy model and assumptions

This project illustrates **pure epsilon-DP** Laplace mechanisms under replace-one/add-remove sensitivity assumptions. Histograms use unit L1 sensitivity when each individual contributes at most one categorical record. Bounded sums use sensitivity `upper - lower` under replace-one neighboring datasets with a fixed public population size. The returned mean divides a noisy sum by that public count. Basic sequential composition adds epsilons; this is not an advanced privacy accountant.

Do not treat the synthetic seeded CLI as a secure private release: deterministic PRNG outputs can be reconstructed. API randomness uses `SystemRandom`, but per-request ledgers reset and therefore cannot enforce a global budget. Outputs are not clipped after adding noise; negative noisy counts are expected. This reference implementation does not handle privacy amplification, subsampling, or secure random-number verification.
