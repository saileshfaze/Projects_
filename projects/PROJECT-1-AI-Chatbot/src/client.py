import os

_client = None


def get_client():
    global _client
    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set.")
        # Import the top-level app module at call-time so tests can patch
        # `app.OpenAI` and have that patched value used here.
        import app as _top_app

        _client = _top_app.OpenAI(api_key=api_key)
    return _client


def fake_reply(message: str) -> str:
    """Return a plausible-looking demo reply when no API key is configured."""
    msg = message.lower()
    if any(w in msg for w in ("hello", "hi", "hey")):
        return (
            "Hello! I'm your AI assistant running in demo mode. "
            "How can I help you today?"
        )
    if "python" in msg:
        return (
            "Python is a versatile, beginner-friendly language widely used for "
            "web development, data science, automation, and AI. Its clean syntax "
            "makes it a great first language to learn!"
        )
    if any(w in msg for w in ("what", "how", "why", "explain")):
        return (
            f"Great question about '{message}'! "
            "In a real session the AI would provide a detailed, context-aware answer. "
            "Add an OPENAI_API_KEY to your .env file to enable live responses."
        )
    return (
        f'You said: "{message}". '
        "This is a demo response — add an OPENAI_API_KEY to your .env "
        "file to get real AI replies."
    )
