"""Local microbenchmark, not a performance guarantee."""
import time

from app.core import evaluate_samples

rows = [{"id": i, "amount": i / 3} for i in range(1000)]
start = time.perf_counter()
result = evaluate_samples(rows, rows)
print(f"duration_ms={(time.perf_counter() - start) * 1000:.2f}, verdict={result['verdict']}")
