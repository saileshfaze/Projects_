from resonance.batch import ingest_directory
from resonance.catalog import Catalog

def test_batch(tmp_path, melody, chirp):
    (tmp_path/"a.wav").write_bytes(melody)
    (tmp_path/"b.wav").write_bytes(chirp)
    (tmp_path/"broken.wav").write_bytes(b"garbage")
    db=Catalog()
    result=ingest_directory(db,tmp_path)
    assert result["added"]==2 and len(result["errors"])==1
    again=ingest_directory(db,tmp_path)
    assert again["duplicates"]==2
    db.close()

def test_nonexistent(tmp_path):
    db=Catalog()
    try:
        import pytest
        with pytest.raises(ValueError): ingest_directory(db,tmp_path/"missing")
    finally: db.close()
