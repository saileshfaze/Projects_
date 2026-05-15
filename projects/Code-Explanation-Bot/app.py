import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from openai import OpenAI

load_dotenv(Path(__file__).parent / ".env")

app = Flask(__name__)

_client = None
DEMO_MODE = not os.getenv("OPENAI_API_KEY")


def get_client():
    global _client
    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set.")
        _client = OpenAI(api_key=api_key)
    return _client


def fake_response(language: str) -> dict:
    return {
        "summary": (
            f"This {language} code defines a function that processes input data and returns a result. "
            "It follows standard patterns for the language and appears to implement a common algorithm."
        ),
        "bugs": [
            "Consider adding input validation to handle edge cases like None or empty inputs.",
            "The loop may not handle the last element correctly — check boundary conditions.",
        ],
        "optimizations": [
            "Use a dictionary/hash map instead of a nested loop to reduce time complexity.",
            "Consider using built-in functions which are typically faster than manual loops.",
        ],
        "demo": True,
    }


@app.route("/")
def index():
    return render_template("index.html", demo_mode=DEMO_MODE)


@app.route("/api/explain", methods=["POST"])
def api_explain():
    data = request.get_json() or {}
    code = (data.get("code") or "").strip()
    language = (data.get("language") or "Python").strip()

    if not code:
        return jsonify({"error": "code is required"}), 400

    if DEMO_MODE:
        return jsonify(fake_response(language))

    prompt = (
        f"You are an expert {language} developer and code reviewer.\n\n"
        f"Analyze the following {language} code:\n\n```{language.lower()}\n{code}\n```\n\n"
        "Respond ONLY with a JSON object (no markdown fences):\n"
        "{\n"
        '  "summary": "<clear plain-English explanation of what the code does, 2-3 sentences>",\n'
        '  "bugs": ["<potential bug or issue 1>", "<potential bug or issue 2>"],\n'
        '  "optimizations": ["<optimization idea 1>", "<optimization idea 2>"]\n'
        "}"
    )

    try:
        client = get_client()
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert code reviewer. Always respond with valid JSON only."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
        )
    except Exception:
        result = fake_response(language)
        result["demo"] = True
        return jsonify(result)

    import json

    raw = response.choices[0].message.content.strip()
    if raw.startswith("```"):
        raw = raw.split("```", 2)[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip().rstrip("```").strip()

    try:
        result = json.loads(raw)
    except Exception:
        return jsonify({"error": "Failed to parse AI response", "raw": raw}), 500

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True, port=5003)
