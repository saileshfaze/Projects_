import pytest
from resonance.catalog import Catalog
from resonance.synthetic import make_clip

@pytest.fixture
def db():
    c=Catalog()
    yield c
    c.close()

def test_ingest_and_get(db, melody):
    row=db.ingest("melody", melody)
    assert row["landmarks"]>0
    assert db.get(row["id"])["sha256"]==row["sha256"]

def test_dedup(db, melody):
    a=db.ingest("a", melody)
    b=db.ingest("b", melody)
    assert a["id"]==b["id"] and b["deduplicated"]
    assert len(db.list_clips())==1

def test_search_self(db, melody, chirp):
    a=db.ingest("melody", melody)
    db.ingest("chirp", chirp)
    results=db.search(melody)
    assert results and results[0]["clip_id"]==a["id"]
    assert results[0]["offset_frames"]==0

def test_delete_cascade(db, melody):
    row=db.ingest("a", melody)
    assert db.delete(row["id"])
    assert db.search(melody)==[]
    assert not db.delete(row["id"])

def test_unknown(db):
    assert db.get("none") is None

def test_list_sorted(db, melody, chirp):
    db.ingest("z", melody)
    db.ingest("a", chirp)
    assert [x["name"] for x in db.list_clips()]==["a","z"]

def test_invalid_name(db, melody):
    with pytest.raises(ValueError): db.ingest("", melody)

def test_invalid_limit(db, melody):
    with pytest.raises(ValueError): db.search(melody, 0)

def test_empty_clip(db):
    from resonance.waveio import encode_wav
    with pytest.raises(ValueError): db.ingest("empty", encode_wav([]))

def test_disk_persistence(tmp_path, melody):
    path=tmp_path/"catalog.db"
    db=Catalog(path); a=db.ingest("a",melody); db.close()
    db=Catalog(path); assert db.get(a["id"]); db.close()
