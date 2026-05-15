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


def fake_response(question: str, level: str) -> dict:
    return {
        "explanation": (
            f"Great question! Here is a {level}-level explanation:\n\n"
            f"When learning about '{question}', it helps to start with the fundamentals. "
            "The core concept involves understanding how the pieces fit together. "
            "Think of it like building blocks — each piece supports the next.\n\n"
            "In Python, this is typically done using straightforward syntax that is easy to read. "
            "Once you grasp the basics, you will be able to apply the concept in real projects."
        ),
        "practice_questions": [
            f"Write a Python function that demonstrates the concept of '{question}'.",
            f"Explain {question} in your own words with a real-world analogy.",
            f"What are three practical applications of {question}?",
        ],
        "next_topics": [
            "Functions and scope",
            "Object-oriented programming",
            "Error handling and exceptions",
        ],
        "demo": True,
    }


@app.route("/")
def index():
    return render_template("index.html", demo_mode=DEMO_MODE)


@app.route("/api/learn", methods=["POST"])
def api_learn():
    data = request.get_json() or {}
    question = (data.get("question") or "").strip()
    level = (data.get("level") or "beginner").strip()

    if not question:
        return jsonify({"error": "question is required"}), 400

    if DEMO_MODE:
        return jsonify(fake_response(question, level))

    prompt = (
        f"You are a friendly and patient Python tutor. A {level} student asks: \"{question}\"\n\n"
        "Provide:\n"
        "1. A clear, encouraging explanation tailored to their level\n"
        "2. Three practice questions to reinforce the concept\n"
        "3. Three suggested next topics to learn\n\n"
        "Respond ONLY with a JSON object (no markdown fences):\n"
        "{\n"
        '  "explanation": "<2-3 paragraph explanation with a Python example if relevant>",\n'
        '  "practice_questions": ["q1", "q2", "q3"],\n'
        '  "next_topics": ["topic1", "topic2", "topic3"]\n'
        "}"
    )

    try:
        client = get_client()
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a friendly Python tutor. Always respond with valid JSON only."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.5,
        )
    except Exception:
        result = fake_response(question, level)
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
    app.run(debug=True, port=5008)
