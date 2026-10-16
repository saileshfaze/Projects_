"""Small reproducible local benchmark; not a production performance claim."""

from datetime import datetime, timedelta, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
from time import perf_counter

from aegis_feature_store.models import FeatureEvent, FeatureView, Observation
from aegis_feature_store.store import FeatureStore


with TemporaryDirectory() as temp:
    store = FeatureStore(str(Path(temp) / "benchmark.db"))
    store.register(FeatureView(
        name="bench_features", version=1, fields={"value": "number"}, ttl_seconds=86400
    ))
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    events = [
        FeatureEvent(
            event_id=f"e{i}", entity_key=f"user-{i % 100}",
            event_ts=(start + timedelta(seconds=i)).isoformat(),
            available_ts=(start + timedelta(seconds=i + 1)).isoformat(),
            values={"value": i / 1000},
        )
        for i in range(1000)
    ]
    t0 = perf_counter()
    store.ingest("bench_features", 1, events)
    ingest_seconds = perf_counter() - t0
    queries = [
        Observation(entity_key=f"user-{i % 100}",
                    as_of=(start + timedelta(seconds=1100)).isoformat())
        for i in range(1000)
    ]
    t0 = perf_counter()
    store.offline_join("bench_features", 1, queries)
    join_seconds = perf_counter() - t0
    print({"events": len(events), "ingest_seconds": round(ingest_seconds, 3),
           "joins": len(queries), "join_seconds": round(join_seconds, 3)})
