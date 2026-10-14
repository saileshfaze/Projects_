import pytest

from atlasflow.db import Store
from atlasflow.schemas import DatasetCreate, Evaluation, PromotionPolicy, RunCreate
from atlasflow.service import DomainError, RegistryService


@pytest.fixture
def service(tmp_path):
    return RegistryService(Store(str(tmp_path / "atlas.sqlite3")))


def dataset(service):
    return service.register_dataset(DatasetCreate(
        name="test", sha256="a" * 64, row_count=100
    ))


def new_run(service, dataset_id, key=None):
    return service.create_run(RunCreate(
        dataset_id=dataset_id, model_name="churn-model", algorithm="logistic",
        seed=42, config={"alpha": 0.1}, idempotency_key=key
    ))


def evaluate(service, run_id, f1=0.9, psi=0.1):
    return service.evaluate(run_id, Evaluation(
        accuracy=0.9, precision=0.9, recall=0.9, f1=f1, drift_psi=psi
    ))


def test_dataset_deduplication_and_lineage(service):
    ds = dataset(service)
    assert dataset(service)["id"] == ds["id"]
    run = new_run(service, ds["id"])
    assert service.lineage(run["id"])["dataset"]["sha256"] == "a" * 64


def test_idempotency_key_reuse_requires_same_payload(service):
    ds = dataset(service)
    key = "client-request-1234"
    first = new_run(service, ds["id"], key)
    assert new_run(service, ds["id"], key)["id"] == first["id"]
    with pytest.raises(DomainError):
        service.create_run(RunCreate(
            dataset_id=ds["id"], model_name="other-model", algorithm="logistic",
            seed=42, idempotency_key=key
        ))


def test_promotion_and_non_regression_gate(service):
    ds = dataset(service)
    first = new_run(service, ds["id"])
    evaluate(service, first["id"], f1=0.92)
    assert service.promote(first["id"], PromotionPolicy())["accepted"]
    second = new_run(service, ds["id"])
    evaluate(service, second["id"], f1=0.80)
    decision = service.promote(second["id"], PromotionPolicy())
    assert not decision["accepted"]
    assert "f1_regression_against_champion" in decision["reasons"]
    assert service.get_champion("churn-model")["id"] == first["id"]
    assert service.audit(second["id"])[0]["accepted"] is False


def test_promote_replaces_champion_atomically(service):
    ds = dataset(service)
    first = new_run(service, ds["id"])
    evaluate(service, first["id"], f1=0.85)
    service.promote(first["id"], PromotionPolicy())
    second = new_run(service, ds["id"])
    evaluate(service, second["id"], f1=0.95)
    assert service.promote(second["id"], PromotionPolicy())["accepted"]
    assert service.get_run(first["id"])["status"] == "archived"
    assert service.get_champion("churn-model")["id"] == second["id"]


def test_evaluation_immutable_and_status_gate(service):
    ds = dataset(service)
    run = new_run(service, ds["id"])
    with pytest.raises(DomainError):
        service.promote(run["id"], PromotionPolicy())
    evaluate(service, run["id"])
    with pytest.raises(DomainError):
        evaluate(service, run["id"])


def test_drift_gate_rejection_is_audited(service):
    ds = dataset(service)
    run = new_run(service, ds["id"])
    evaluate(service, run["id"], psi=0.9)
    decision = service.promote(run["id"], PromotionPolicy())
    assert decision["reasons"] == ["drift_exceeds_limit"]
    assert service.get_run(run["id"])["status"] == "rejected"
    assert len(service.audit(run["id"])) == 1
