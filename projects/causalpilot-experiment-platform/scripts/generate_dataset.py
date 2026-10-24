"""Regenerate checked-in synthetic event sample."""
from pathlib import Path
from causalpilot.models import Experiment
from causalpilot.synthetic import generate, write_csv


def main():
    config=Experiment("checkout-demo","synthetic-only-demo-salt")
    path=Path(__file__).resolve().parents[1]/"data"/"sample_events.csv"
    write_csv(generate(config,n=80,seed=42),path)
    print(path)


if __name__=="__main__":
    main()
