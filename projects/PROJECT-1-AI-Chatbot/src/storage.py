import json

from .config import HISTORY_PATH


def load_history():
    if not HISTORY_PATH.exists():
        HISTORY_PATH.write_text("[]")
    try:
        return json.loads(HISTORY_PATH.read_text())
    except Exception:
        HISTORY_PATH.write_text("[]")
        return []


def save_message(role, content):
    history = load_history()
    history.append({"role": role, "content": content})
    HISTORY_PATH.write_text(json.dumps(history, indent=2))
