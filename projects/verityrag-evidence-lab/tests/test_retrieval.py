import pytest
from verityrag.retrieval import Document, HybridIndex, tokenize

def test_tokenizer():
    assert tokenize("Error-429: retry!") == ["error", "429", "retry"]

def test_relevant_doc_first():
    index = HybridIndex([Document("a", "Cache invalidation", "Invalidate redis cache keys after writes."),
                         Document("b", "Backup rotation", "Rotate database snapshots every day.")])
    assert index.search("redis cache invalidation")[0].document.id == "a"
    assert index.search("something totally unrelated") == []

def test_deterministic_ranking():
    index = HybridIndex([Document("b", "X", "test test"), Document("a", "X", "test test")])
    assert [h.document.id for h in index.search("test")] == ["a", "b"]

def test_duplicate_ids_rejected():
    with pytest.raises(ValueError):
        HybridIndex([Document("a", "A", "one"), Document("a", "B", "two")])

def test_invalid_k_rejected():
    with pytest.raises(ValueError):
        HybridIndex([]).search("test", 0)
