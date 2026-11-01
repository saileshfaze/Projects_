import json
from resonance.cli import main

def test_generate_and_analyze(tmp_path, capsys):
    wav=tmp_path/"test.wav"; svg=tmp_path/"test.svg"
    assert main(["generate",str(wav)])==0
    assert wav.exists()
    assert main(["analyze",str(wav),"--svg",str(svg)])==0
    assert svg.exists() and "duration_s" in capsys.readouterr().out

def test_ingest_and_search(tmp_path, capsys):
    wav=tmp_path/"test.wav"; db=tmp_path/"db.sqlite"
    main(["generate",str(wav)])
    main(["--db",str(db),"ingest",str(wav)])
    main(["--db",str(db),"search",str(wav)])
    assert "aligned_votes" in capsys.readouterr().out
