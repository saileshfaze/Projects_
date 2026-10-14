"""Optional sklearn training with deterministic split and test-only evaluation."""

from atlasflow.metrics import binary_metrics, population_stability_index


def train_and_evaluate(rows: list[dict], seed: int = 42) -> dict:
    try:
        from sklearn.linear_model import LogisticRegression
        from sklearn.model_selection import train_test_split
        from sklearn.pipeline import make_pipeline
        from sklearn.preprocessing import StandardScaler
    except ImportError as error:
        raise RuntimeError("Install the optional ML extras: pip install -e '.[ml]'") from error

    features = [[row["age"], row["usage_hours"], row["incidents"]] for row in rows]
    labels = [row["label"] for row in rows]
    indices = list(range(len(rows)))
    train_idx, test_idx = train_test_split(
        indices, test_size=0.25, random_state=seed, stratify=labels
    )
    model = make_pipeline(StandardScaler(), LogisticRegression(random_state=seed, max_iter=1000))
    model.fit([features[i] for i in train_idx], [labels[i] for i in train_idx])
    predictions = model.predict([features[i] for i in test_idx]).tolist()
    metrics = binary_metrics([labels[i] for i in test_idx], predictions)
    drift = population_stability_index(
        [float(rows[i]["usage_hours"]) for i in train_idx],
        [float(rows[i]["usage_hours"]) for i in test_idx],
        bins=6,
    )
    return {"metrics": metrics, "drift_psi": drift, "train_rows": len(train_idx),
            "test_rows": len(test_idx), "model": model}
