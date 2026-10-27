"""Reproducible strategy comparison and JSON export."""
import json
from pathlib import Path
from voltpilot.synthetic import generate
from voltpilot.models import Site
from voltpilot.dispatch import compare


def main():
    result=compare(generate(days=3,seed=2026,outage_start=160,outage_length=12),Site())
    path=Path("out/benchmark.json");path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    for name,summary in result.items():
        print(f"{name:18} EUR {summary['total_cost_eur']:8.2f}  unserved {summary['unserved_kwh']:7.2f} kWh")


if __name__=="__main__": main()
