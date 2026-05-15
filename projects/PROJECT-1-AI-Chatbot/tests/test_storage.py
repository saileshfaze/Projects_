import json


def test_load_history_creates_file_when_missing(tmp_path, monkeypatch):
    import src.storage as storage

    path = tmp_path / "history.json"
    monkeypatch.setattr(storage, "HISTORY_PATH", path)

    history = storage.load_history()
    assert history == []
    assert path.exists()


def test_load_history_returns_list(tmp_path, monkeypatch):
    import src.storage as storage

    path = tmp_path / "history.json"
    path.write_text(json.dumps([{"role": "user", "content": "hello"}]))
    monkeypatch.setattr(storage, "HISTORY_PATH", path)

    history = storage.load_history()
    assert len(history) == 1
    assert history[0]["role"] == "user"


def test_load_history_recovers_from_corrupt_json(tmp_path, monkeypatch):
    import src.storage as storage

    path = tmp_path / "bad.json"
    path.write_text("NOT JSON{{")
    monkeypatch.setattr(storage, "HISTORY_PATH", path)

    history = storage.load_history()
    assert history == []


def test_save_message_appends(tmp_path, monkeypatch):
    import src.storage as storage

    path = tmp_path / "history.json"
    monkeypatch.setattr(storage, "HISTORY_PATH", path)

    storage.save_message("user", "first")
    storage.save_message("assistant", "second")

    data = json.loads(path.read_text())
    assert len(data) == 2
    assert data[0] == {"role": "user", "content": "first"}
    assert data[1] == {"role": "assistant", "content": "second"}
