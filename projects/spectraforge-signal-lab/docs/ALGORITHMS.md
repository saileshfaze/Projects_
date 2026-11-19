# Numerical design and assumptions

## FFT

Recursive radix-2 decimation in time with the negative-sign forward transform. Runtime O(N log N); recursion and allocations make it slower than optimized native libraries.

## Window and amplitudes

Hann uses symmetric endpoints. The spectrum divides by the sum of window coefficients (coherent gain), doubles non-DC/non-Nyquist positive bins, and reports frequency k·Fs/N. Amplitude is accurate for bin-centered pure sinusoids but not arbitrary off-bin tones.

## Peak selection

Local maxima exclude DC and rank by amplitude, then ascending frequency. This is not statistical significance testing.

## Anomalies

The rolling baseline excludes the current sample to avoid look-ahead leakage. Population variance is floored by 1e-9 in standard deviation units. A periodic waveform can create false positives; production detectors need domain-specific validation.

## Reproducibility

`random.Random(seed)` drives Gaussian noise; no external files or telemetry. Results may differ slightly between Python implementations because of floating-point math.
