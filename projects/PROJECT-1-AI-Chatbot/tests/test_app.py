import json
from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _no_api_key(monkeypatch):
    """Ensure tests always run in DEMO_MODE (no real API calls)."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)


@pytest.fixture()
def client(tmp_path, monkeypatch):
    """Flask test client with an isolated chat_history.json in a temp dir."""
    import app as application

    monkeypatch.setattr(application, "HISTORY_PATH", tmp_path / "chat_history.json")
    monkeypatch.setattr(application, "DEMO_MODE", True)

    application.app.config["TESTING"] = True
    with application.app.test_client() as c:
        yield c


# ---------------------------------------------------------------------------
# fake_reply unit tests
# ---------------------------------------------------------------------------


class TestFakeReply:
    def test_greeting_hi(self):
        from app import fake_reply

        assert "demo mode" in fake_reply("hi").lower()

    def test_greeting_hello(self):
        from app import fake_reply

        assert "assistant" in fake_reply("Hello there").lower()

    def test_greeting_hey(self):
        from app import fake_reply

        assert "assistant" in fake_reply("hey!").lower()

    def test_python_keyword(self):
        from app import fake_reply

        reply = fake_reply("Tell me about Python")
        assert "python" in reply.lower()

    def test_question_what(self):
        from app import fake_reply

        # avoid words containing 'hi'/'hey'/'hello' substrings (e.g. 'machine', 'this')
        reply = fake_reply("What is the capital of France?")
        assert "great question" in reply.lower()

    def test_question_how(self):
        from app import fake_reply

        reply = fake_reply("How do generators work?")
        assert "great question" in reply.lower()

    def test_fallback(self):
        from app import fake_reply

        msg = "random unrecognised input 12345"
        reply = fake_reply(msg)
        assert msg in reply


# ---------------------------------------------------------------------------
# History helpers
# ---------------------------------------------------------------------------


class TestHistory:
    def test_load_history_creates_file_when_missing(self, tmp_path, monkeypatch):
        import app as application

        monkeypatch.setattr(application, "HISTORY_PATH", tmp_path / "new_history.json")
        history = application.load_history()
        assert history == []
        assert (tmp_path / "new_history.json").exists()

    def test_load_history_returns_list(self, tmp_path, monkeypatch):
        import app as application

        path = tmp_path / "history.json"
        path.write_text(json.dumps([{"role": "user", "content": "hello"}]))
        monkeypatch.setattr(application, "HISTORY_PATH", path)
        history = application.load_history()
        assert len(history) == 1
        assert history[0]["role"] == "user"

    def test_load_history_recovers_from_corrupt_json(self, tmp_path, monkeypatch):
        import app as application

        path = tmp_path / "bad.json"
        path.write_text("NOT JSON{{")
        monkeypatch.setattr(application, "HISTORY_PATH", path)
        history = application.load_history()
        assert history == []

    def test_save_message_appends(self, tmp_path, monkeypatch):
        import app as application

        path = tmp_path / "history.json"
        monkeypatch.setattr(application, "HISTORY_PATH", path)
        application.save_message("user", "first")
        application.save_message("assistant", "second")
        data = json.loads(path.read_text())
        assert len(data) == 2
        assert data[0] == {"role": "user", "content": "first"}
        assert data[1] == {"role": "assistant", "content": "second"}


# ---------------------------------------------------------------------------
# Flask route tests
# ---------------------------------------------------------------------------


class TestIndexRoute:
    def test_get_returns_200(self, client):
        resp = client.get("/")
        assert resp.status_code == 200


class TestHistoryRoute:
    def test_empty_history(self, client):
        resp = client.get("/api/history")
        assert resp.status_code == 200
        assert resp.get_json() == []

    def test_history_after_chat(self, client):
        client.post("/api/chat", json={"message": "hello"})
        resp = client.get("/api/history")
        data = resp.get_json()
        assert any(m["role"] == "user" for m in data)


class TestChatRoute:
    def test_empty_message_returns_400(self, client):
        resp = client.post("/api/chat", json={"message": ""})
        assert resp.status_code == 400
        assert "error" in resp.get_json()

    def test_missing_message_key_returns_400(self, client):
        resp = client.post("/api/chat", json={})
        assert resp.status_code == 400

    def test_whitespace_only_message_returns_400(self, client):
        resp = client.post("/api/chat", json={"message": "   "})
        assert resp.status_code == 400

    def test_demo_mode_reply(self, client):
        resp = client.post("/api/chat", json={"message": "hi"})
        assert resp.status_code == 200
        body = resp.get_json()
        assert "reply" in body
        assert body.get("demo") is True

    def test_python_topic_demo_reply(self, client):
        resp = client.post("/api/chat", json={"message": "Tell me about Python"})
        body = resp.get_json()
        assert resp.status_code == 200
        assert "python" in body["reply"].lower()

    def test_reply_saved_to_history(self, client):
        client.post("/api/chat", json={"message": "hello"})
        resp = client.get("/api/history")
        roles = [m["role"] for m in resp.get_json()]
        assert "user" in roles
        assert "assistant" in roles

    def test_non_json_body_returns_415(self, client):
        # Flask rejects unknown content-types with 415 Unsupported Media Type
        resp = client.post("/api/chat", data="plain text", content_type="text/plain")
        assert resp.status_code == 415

    def test_get_client_raises_without_key(self, monkeypatch):
        import app as application

        monkeypatch.setattr(application, "_client", None)
        with pytest.raises(ValueError, match="OPENAI_API_KEY"):
            application.get_client()

    def test_live_mode_uses_openai(self, tmp_path, monkeypatch):
        """When an API key is set, the real OpenAI client path is exercised (mocked)."""
        import app as application

        monkeypatch.setenv("OPENAI_API_KEY", "test-key-123")
        monkeypatch.setattr(application, "DEMO_MODE", False)
        monkeypatch.setattr(application, "HISTORY_PATH", tmp_path / "history.json")
        monkeypatch.setattr(application, "_client", None)

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content="  mocked AI reply  "))]
        )

        with patch("app.OpenAI", return_value=mock_client):
            application.app.config["TESTING"] = True
            with application.app.test_client() as c:
                resp = c.post("/api/chat", json={"message": "What is AI?"})

        assert resp.status_code == 200
        body = resp.get_json()
        assert body["reply"] == "mocked AI reply"
        assert "demo" not in body
