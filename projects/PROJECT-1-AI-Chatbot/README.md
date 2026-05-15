# Simple AI Chatbot

A minimal chatbot demo using the OpenAI API, Flask backend, and a small web frontend.

## Prerequisites

- Python 3.8+
- An OpenAI API key — get one at https://platform.openai.com/api-keys

## Quick Start

**1. Create and activate a virtual environment**

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows CMD/PowerShell
source .venv/Scripts/activate # Git Bash / WSL
```

**2. Install dependencies**

```bash
pip install -r requirements.txt
```

**3. Add your API key to `.env`**

Open `.env` and replace the placeholder with your real key:

```
OPENAI_API_KEY=sk-...your-real-key...
```

> Never commit `.env` to version control — add it to `.gitignore`.

**4. Run the server**

```bash
python app.py
```

**5. Open in browser**

http://127.0.0.1:5000

## Files

| File | Purpose |
|------|---------|
| `app.py` | Flask backend — OpenAI API calls, history read/write |
| `.env` | API key (not committed) |
| `templates/index.html` | Chat UI |
| `static/script.js` | Client-side send/receive logic |
| `static/style.css` | Styles |
| `chat_history.json` | Persisted conversation history |
| `requirements.txt` | Python dependencies |
