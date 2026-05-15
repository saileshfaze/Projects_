"""Backward-compatible top-level module and launcher.

This file is a thin compatibility layer that exposes the original
names used by the test-suite and previous code (e.g. `fake_reply`,
`load_history`, `save_message`, `get_client`, `HISTORY_PATH`, etc.) while
delegating the implementation into the `src` package.
"""

import os

from openai import OpenAI

from src import app as _flask_app
from src import client as _client_mod
from src import config as _config_mod

# Flask application (kept name `app` for compatibility)
app = _flask_app


# Backwards-compatible names expected by tests / external imports
HISTORY_PATH = _config_mod.HISTORY_PATH
DEMO_MODE = _config_mod.DEMO_MODE

# Local client handle (tests mutate this)
_client = _client_mod._client

notes: Str= 'hello'

def get_client():
    """Compatibility wrapper around client.get_client().

    The original tests expect `get_client()` and a module-level
    `_client` variable to exist on `app` — keep that behaviour.
    """
    global _client
    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set.")
        _client = OpenAI(api_key=api_key)
    return _client


def fake_reply(message: str) -> str:
    return _client_mod.fake_reply(message)


def load_history():
    # Use the top-level HISTORY_PATH so tests can monkeypatch it.
    path = HISTORY_PATH
    if not path.exists():
        path.write_text("[]")
    try:
        import json

        return json.loads(path.read_text())
    except Exception:
        path.write_text("[]")
        return []


def save_message(role, content):
    # Use the top-level HISTORY_PATH so tests can monkeypatch it.
    import json

    history = load_history()
    history.append({"role": role, "content": content})
    HISTORY_PATH.write_text(json.dumps(history, indent=2))


# Expose OpenAI symbol so tests can patch `app.OpenAI`
OpenAI = OpenAI


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)
