"""Chronological ML demo using leakage-safe synthetic features.

Requires: pip install -e '.[ml]'
"""

import json
from pathlib import Path
from tempfile import TemporaryDirectory

from aegis_feature_store.models import FeatureEvent, FeatureView, Observation
from aegis_feature_store.store import FeatureStore

try:
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import roc_auc_score
except ImportError as exc:
    raise SystemExit("Install the optional ML extra: pip install -e '.[ml]'") from exc

ROOT = Path(__file__).resolve().parents[1]
generated = ROOT / "data/generated"
if not (generated / "events.json").exists():
    raise SystemExit("First run: python scripts/generate_data.py")

with TemporaryDirectory() as tmp:
    store = FeatureStore(str(Path(tmp) / "demo.db"))
    store.register(FeatureView.model_validate_json(
        (ROOT / "data/customer_risk_view.json").read_text()
    ))
    events = json.loads((generated / "events.json").read_text())
    # SQLite batches keep the example bounded and easy to inspect.
    for offset in range(0, len(events), 500):
        store.ingest("customer_risk", 1, [
            FeatureEvent.model_validate(e) for e in events[offset:offset + 500]
        ])
    labels = json.loads((generated / "labels.json").read_text())
    observations = [Observation(entity_key=x["entity_key"], as_of=x["as_of"])
                    for x in labels]
    joined = store.offline_join("customer_risk", 1, observations)
    samples = [
        (x["as_of"], [row["features"]["score"], row["features"]["count"],
                       int(row["features"]["active"])], x["label"])
        for x, row in zip(labels, joined) if row["features"] is not None
    ]
    samples.sort(key=lambda x: x[0])
    cutoff = int(0.8 * len(samples))
    train, test = samples[:cutoff], samples[cutoff:]
    if not train or not test or len(set(x[2] for x in train)) < 2:
        raise SystemExit("Not enough balanced samples for chronological training")
    model = LogisticRegression(max_iter=500, random_state=42)
    model.fit([x[1] for x in train], [x[2] for x in train])
    probabilities = model.predict_proba([x[1] for x in test])[:, 1]
    if len(set(x[2] for x in test)) < 2:
        raise SystemExit("Test period has only one class; cannot calculate ROC AUC")
    print(json.dumps({
        "train_rows": len(train), "test_rows": len(test),
        "roc_auc_synthetic": round(roc_auc_score([x[2] for x in test], probabilities), 4),
        "disclaimer": "Synthetic labels; not a real-world predictive-performance estimate.",
    }, indent=2))
