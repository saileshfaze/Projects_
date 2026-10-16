import pytest

from aegis_feature_store.models import FeatureView
from aegis_feature_store.store import StoreError


def test_register_and_list(store):
    views = store.list_views()
    assert len(views) == 1
    assert views[0]["fields"]["score"] == "number"


def test_register_duplicate_rejected(store):
    with pytest.raises(StoreError, match="already registered"):
        store.register(FeatureView(name="customer_risk", version=1,
                                   fields={"score": "number"}, ttl_seconds=60))


def test_version_isolation(store):
    store.register(FeatureView(name="customer_risk", version=2,
                               fields={"score": "number"}, ttl_seconds=60))
    assert len(store.list_views()) == 2
