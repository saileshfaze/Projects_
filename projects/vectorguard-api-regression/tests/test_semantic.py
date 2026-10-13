import pytest

from app.semantic import compare_text


def test_offline_similarity():
    result = compare_text("hello world", "hello world")
    assert result["backend"] == "lexical"
    assert result["similarity"] == 1.0


def test_embedding_requires_local_model():
    with pytest.raises(ValueError):
        compare_text("hello", "world", backend="embedding", model_path="/no/such/model")


def test_unknown_backend():
    with pytest.raises(ValueError):
        compare_text("hello", "world", backend="unknown")
