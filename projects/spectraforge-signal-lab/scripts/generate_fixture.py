from pathlib import Path
import csv
from spectraforge.core import generate_signal
out = Path("data/synthetic_signal.csv")
out.parent.mkdir(exist_ok=True)
signal = generate_signal(128, 128, [(8, 1.0), (24, 0.3)], 0.02, 2026)
with out.open("w", newline="") as f:
    writer = csv.writer(f); writer.writerow(["sample", "amplitude"])
    writer.writerows(enumerate(signal))
print(out)
