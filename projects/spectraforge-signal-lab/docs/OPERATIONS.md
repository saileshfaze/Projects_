# Operations

Run `python -m spectraforge.cli --output output/report.json --csv output/signal.csv` after installation. Avoid passing user-supplied unbounded sample sizes: the recursive reference FFT consumes memory and CPU. Do not treat synthetic anomaly scores as safety alerts. For production-grade signal analysis use validated, vectorized libraries and independent numerical benchmarks.
