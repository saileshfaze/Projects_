import os
from pathlib import Path

from dotenv import load_dotenv

# .env is in the project root (AI-Chatbot), src is one level deeper
ROOT = Path(__file__).parent.parent
load_dotenv(ROOT / ".env")

HISTORY_PATH = ROOT / "chat_history.json"
DEMO_MODE = not os.getenv("OPENAI_API_KEY")
