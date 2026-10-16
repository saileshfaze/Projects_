import pytest

from aegis_feature_store.models import FeatureView
from aegis_feature_store.store import FeatureStore


@pytest.fixture
def store(tmp_path):
    instance = FeatureStore(str(tmp_path / "features.db"))
    instance.register(
        FeatureView(
            name="customer_risk",
            version=1,
            fields={"score": "number", "count": "integer", "active": "boolean"},
            ttl_seconds=86400,
            description="Synthetic customer-risk features",
        )
    )
    return instance
