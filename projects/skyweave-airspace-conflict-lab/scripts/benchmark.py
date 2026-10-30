"""Synthetic performance smoke benchmark; results depend on local hardware."""
from time import perf_counter
from skyweave.scenarios import crossing
from skyweave.detector import detect
from skyweave.uncertainty import sample_risk

flights=crossing();start=perf_counter()
for _ in range(100):detect(flights)
print(f'100 detector runs: {perf_counter()-start:.4f}s')
start=perf_counter();sample_risk(flights,samples=100,seed=42)
print(f'100 Monte Carlo trials: {perf_counter()-start:.4f}s')
