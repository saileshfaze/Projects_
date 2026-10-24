"""Run an isolated reproducible demo, emitting an evidence JSON file."""
import json
import tempfile
from pathlib import Path
from causalpilot.models import Experiment
from causalpilot.service import ExperimentService
from causalpilot.synthetic import generate


def main() -> None:
    config=Experiment("checkout-demo","synthetic-only-demo-salt",minimum_per_arm=20)
    with tempfile.TemporaryDirectory() as directory:
        service=ExperimentService(str(Path(directory)/"demo.sqlite3"))
        service.register(config)
        events=generate(config,n=800,seed=42)
        assert sum(service.ingest(e) for e in events)==800
        assert sum(service.ingest(e) for e in events)==0
        report=service.report(config.experiment_id)
        assert report["eligible"]
        print(json.dumps(report,indent=2))


if __name__=="__main__":
    main()
