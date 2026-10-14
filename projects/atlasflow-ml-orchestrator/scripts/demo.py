"""End-to-end synthetic training, artifact manifest, evaluation and promotion."""

import argparse
import json
from pathlib import Path

from atlasflow.db import Store
from atlasflow.fingerprints import sha256_file, sha256_records
from atlasflow.schemas import DatasetCreate, Evaluation, PromotionPolicy, RunCreate
from atlasflow.service import RegistryService
from atlasflow.synthetic import make_rows, write_csv
from atlasflow.training import train_and_evaluate


def run_demo(db_path: str, output_dir: str) -> dict:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    rows = make_rows(count=320, seed=2026)
    dataset_path = output / "synthetic_customers.csv"
    write_csv(dataset_path, rows)

    service = RegistryService(Store(db_path))
    dataset = service.register_dataset(DatasetCreate(
        name="synthetic-customer-retention",
        sha256=sha256_records(rows),
        row_count=len(rows),
    ))
    run = service.create_run(RunCreate(
        dataset_id=dataset["id"],
        model_name="customer-retention",
        algorithm="sklearn-logistic-regression",
        seed=42,
        config={"split": 0.25, "scaler": "standard"},
    ))
    result = train_and_evaluate(rows, seed=42)
    model = result["model"]
    scaler = model.named_steps["standardscaler"]
    classifier = model.named_steps["logisticregression"]
    manifest = {
        "run_id": run["id"],
        "dataset_sha256": dataset["sha256"],
        "features": ["age", "usage_hours", "incidents"],
        "scaler_mean": scaler.mean_.tolist(),
        "scaler_scale": scaler.scale_.tolist(),
        "coefficients": classifier.coef_.tolist(),
        "intercept": classifier.intercept_.tolist(),
        "classes": classifier.classes_.tolist(),
        "train_rows": result["train_rows"],
        "test_rows": result["test_rows"],
    }
    artifact_path = output / f"model_manifest_{run['id']}.json"
    artifact_path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    evaluation = service.evaluate(run["id"], Evaluation(
        **result["metrics"], drift_psi=result["drift_psi"],
        artifact_sha256=sha256_file(artifact_path),
    ))
    decision = service.promote(run["id"], PromotionPolicy(
        min_accuracy=0.70, min_f1=0.70, max_drift_psi=1.0,
    ))
    return {"dataset": dataset, "run": evaluation, "promotion": decision,
            "artifact": str(artifact_path)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", default="var/atlasflow.sqlite3")
    parser.add_argument("--output", default="var/demo")
    args = parser.parse_args()
    print(json.dumps(run_demo(args.db, args.output), indent=2))
