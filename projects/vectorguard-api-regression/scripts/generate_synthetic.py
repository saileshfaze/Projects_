"""Generate deterministic synthetic response fixtures."""
import json
import random
from pathlib import Path

random.seed(2026)
root = Path(__file__).resolve().parents[1] / 'data'
root.mkdir(exist_ok=True)
baseline = [{'id': 1000 + i, 'total': round(random.uniform(8, 75), 2), 'message': 'payment accepted'} for i in range(40)]
candidate = [{**row, 'total': str(row['total']), 'message': 'payment delayed'} for row in baseline]
for name, rows in [('baseline_orders.json', baseline), ('candidate_orders.json', candidate)]:
    (root / name).write_text(json.dumps(rows, indent=2) + '\n', encoding='utf-8')
