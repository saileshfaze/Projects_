import time
from spectraforge.core import generate_signal, spectrum
for n in (128, 512, 2048):
    data = generate_signal(n, 4096, [(128, 1)])
    start = time.perf_counter()
    for _ in range(10): spectrum(data, 4096)
    print(f"n={n} ten_runs_seconds={time.perf_counter()-start:.6f}")
