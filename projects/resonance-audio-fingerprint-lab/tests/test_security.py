import sqlite3
from resonance.catalog import Catalog

def test_sql_injection_name_is_data(melody):
    db=Catalog()
    db.ingest("'); DROP TABLE clips; --",melody)
    assert len(db.list_clips())==1
    db.close()

def test_no_audio_blob_storage(melody):
    db=Catalog()
    db.ingest("test",melody)
    cols=[row[1] for row in db.conn.execute("PRAGMA table_info(clips)")]
    assert "audio" not in cols and "wav" not in cols
    db.close()
