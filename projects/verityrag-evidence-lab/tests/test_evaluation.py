import pytest
from verityrag.evaluation import ranking_metrics, bootstrap_ci, evaluate
from verityrag.retrieval import Document, HybridIndex

def test_ranking_metrics():
    result = ranking_metrics(["b", "a", "c"], {"a", "c"}, 3)
    assert result["recall"] == 1.0
    assert result["mrr"] == 0.5
    assert 0 < result["ndcg"] < 1

def test_bootstrap_reproducible():
    assert bootstrap_ci([0.0, 1.0, 1.0]) == bootstrap_ci([0.0, 1.0, 1.0])

def test_slices():
    idx = HybridIndex([Document("a", "Cache", "Redis cache expiry"), Document("b", "Billing", "Invoice cycles")])
    report = evaluate(idx, [{"id": "q1", "question": "redis cache", "slice": "ops"}], {"q1": {"a"}}, 2)
    assert report["overall"]["recall"] == 1.0
    assert report["slices"]["ops"]["queries"] == 1

def test_empty_evaluation_rejected():
    with pytest.raises(ValueError):
        evaluate(HybridIndex([]), [], {})
