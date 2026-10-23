import pytest
from verityrag.storage import connect, ingest, all_documents, corpus_hash, save_evaluation
from verityrag.retrieval import Document

def test_ingest_upsert_and_history():
    con = connect(":memory:")
    ingest(con, [Document("a", "A", "First version")])
    before = corpus_hash(con)
    ingest(con, [Document("a", "A", "Second version")])
    assert len(all_documents(con)) == 1
    assert corpus_hash(con) != before
    assert save_evaluation(con, {"ok": True}) == 1
    con.close()

def test_invalid_batch_rolls_back():
    con = connect(":memory:")
    with pytest.raises(ValueError):
        ingest(con, [Document("a", "A", "Valid"), Document("b", "B", "")])
    assert all_documents(con) == []
    con.close()
