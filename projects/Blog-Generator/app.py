import json
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


def fake_response(topic: str, tone: str) -> dict:
    """Return plausible-looking demo data when no API key is configured."""
    title = f"The Ultimate Guide to {topic.title()}"
    content = (
        f"Welcome to this {tone} exploration of {topic}. "
        f"In today's fast-paced world, understanding {topic} has never been more important. "
        f"Whether you're a beginner or a seasoned expert, there is always something new to discover.\n\n"
        f"{topic.capitalize()} has transformed the way we think about everyday challenges. "
        f"From its humble origins to its modern applications, the journey is both fascinating and instructive. "
        f"Pioneers in the field have dedicated years to refining best practices that we now take for granted.\n\n"
        f"One of the key aspects of {topic} is its versatility. It can be applied across industries, "
        f"bridging gaps between technology, creativity, and human connection. "
        f"This adaptability is precisely what makes it such a compelling subject for any audience.\n\n"
        f"Looking ahead, the future of {topic} is bright. Emerging trends suggest continued growth, "
        f"innovation, and increased accessibility. As more people engage with {topic}, "
        f"we can expect a vibrant community of practitioners sharing knowledge and pushing boundaries.\n\n"
        f"In conclusion, {topic} represents a remarkable opportunity for learning and growth. "
        f"By staying curious and open-minded, you can harness its full potential and make a meaningful impact."
    )
    seo_keywords = [
        topic.lower(),
        f"{topic.lower()} guide",
        f"learn {topic.lower()}",
        f"{topic.lower()} tips",
        f"{topic.lower()} 2026",
    ]
    return {"title": title, "content": content, "seo_keywords": seo_keywords, "demo": True}


@app.route("/")
def index():
    return render_template("index.html", demo_mode=DEMO_MODE)


@app.route("/api/generate", methods=["POST"])
def api_generate():
    data = request.get_json() or {}
    topic = (data.get("topic") or "").strip()
    tone = (data.get("tone") or "informative").strip()

    if not topic:
        return jsonify({"error": "topic is required"}), 400

    # --- Demo / fallback mode ---
    if DEMO_MODE:
        return jsonify(fake_response(topic, tone))

    prompt = (
        f"Write a blog post about: {topic}\n"
        f"Tone: {tone}\n\n"
        "Respond ONLY with a JSON object in this exact format (no markdown fences):\n"
        "{\n"
        '  "title": "<catchy blog title>",\n'
        '  "content": "<full blog post, 4-6 paragraphs>",\n'
        '  "seo_keywords": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5"]\n'
        "}"
    )

    try:
        client = get_client()
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert blog writer. "
                        "Always respond with valid JSON only — no markdown, no explanation."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
        )
    except Exception:
        # API call failed — fall back to demo data
        result = fake_response(topic, tone)
        result["demo"] = True
        return jsonify(result)

    raw = response.choices[0].message.content.strip()

    # Strip markdown fences if the model wraps anyway
    if raw.startswith("```"):
        raw = raw.split("```", 2)[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()
        if raw.endswith("```"):
            raw = raw[:-3].strip()

    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        return jsonify({"error": "Failed to parse AI response", "raw": raw}), 500

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True, port=5002)
