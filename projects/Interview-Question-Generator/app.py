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


def fake_response(topic: str, level: str) -> dict:
    return {
        "questions": [
            {
                "question": f"What is {topic} and why is it important?",
                "answer": f"{topic.capitalize()} is a fundamental concept in software development. Understanding it helps developers write better, more efficient code. It is important because it forms the foundation for many advanced topics in the field.",
            },
            {
                "question": f"Explain a common use case for {topic}.",
                "answer": f"A common use case for {topic} is in building scalable applications. Developers use it to solve recurring problems efficiently and maintain clean, readable codebases.",
            },
            {
                "question": f"What are the main advantages of using {topic}?",
                "answer": f"The main advantages include improved performance, better code organization, easier maintenance, and reduced duplication. These benefits make {topic} a valuable skill for any developer.",
            },
            {
                "question": f"How would you implement {topic} in a real project?",
                "answer": f"To implement {topic} in a real project, start by identifying the problem it solves, then apply the relevant patterns or APIs. Always write tests to verify your implementation works as expected.",
            },
            {
                "question": f"What are common pitfalls when working with {topic}?",
                "answer": f"Common pitfalls include over-engineering, ignoring edge cases, not handling errors properly, and failing to document the code. Being aware of these helps you avoid mistakes early in development.",
            },
        ],
        "demo": True,
    }


@app.route("/")
def index():
    return render_template("index.html", demo_mode=DEMO_MODE)


@app.route("/api/generate", methods=["POST"])
def api_generate():
    data = request.get_json() or {}
    topic = (data.get("topic") or "").strip()
    level = (data.get("level") or "intermediate").strip()
    count = min(int(data.get("count") or 5), 10)

    if not topic:
        return jsonify({"error": "topic is required"}), 400

    if DEMO_MODE:
        return jsonify(fake_response(topic, level))

    prompt = (
        f"You are an expert technical interviewer. Generate {count} {level}-level interview questions "
        f"about {topic}, each with a detailed answer and explanation.\n\n"
        "Respond ONLY with a JSON object (no markdown fences):\n"
        '{"questions": [{"question": "...", "answer": "..."}, ...]}'
    )

    try:
        client = get_client()
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert technical interviewer. Always respond with valid JSON only."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.6,
        )
    except Exception:
        result = fake_response(topic, level)
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
    app.run(debug=True, port=5006)
