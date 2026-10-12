"""Generate deterministic synthetic cloud bills; no external data used."""
import csv
import random
from datetime import date, timedelta
from pathlib import Path

random.seed(42)
out = Path('data/synthetic_billing.csv')
out.parent.mkdir(parents=True, exist_ok=True)
with out.open('w', newline='') as handle:
    writer = csv.writer(handle)
    writer.writerow(['date', 'provider', 'service', 'project', 'cost', 'currency'])
    for day in range(90):
        for provider in ('aws', 'azure', 'gcp'):
            writer.writerow([(date(2026, 1, 1) + timedelta(days=day)).isoformat(), provider, 'compute', 'demo', round(random.uniform(4, 35), 2), 'EUR'])
print(out)
