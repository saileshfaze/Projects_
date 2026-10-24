"""Application service coordinating assignment, ingestion and analysis."""
from .models import Experiment, Outcome
from .statistics import analyze
from .store import Ledger


class ExperimentService:
    def __init__(self, db_path: str):
        self.ledger = Ledger(db_path)

    def register(self, config: Experiment) -> None:
        self.ledger.register(config)

    def assign(self, experiment_id: str, subject_id: str) -> str:
        return self.ledger.assign(experiment_id, subject_id)

    def ingest(self, event: Outcome) -> bool:
        return self.ledger.ingest(event)

    def report(self, experiment_id: str, seed: int = 17) -> dict:
        config = self.ledger.config(experiment_id)
        return {"experiment_id":experiment_id, **analyze(self.ledger.rows(experiment_id),self.ledger.counts(experiment_id),config.treatment_fraction,config.alpha,config.planned_looks,config.minimum_per_arm,seed)}
