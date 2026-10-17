# Performance methodology

Run python benchmarks/bench_solver.py to time repeated solves of the committed 24-hour synthetic scenario. The benchmark reports mean and median wall time, number of variables and solver status. Results vary with CPU, SciPy/HiGHS version and solver settings. No performance numbers are claimed without execution. Complexity is worst-case exponential in the number of binary decisions; cap the horizon and use explicit time limits. The reference implementation is intended for scenario planning rather than sub-second online dispatch.
