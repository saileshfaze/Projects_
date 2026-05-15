import os
import re
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


def extract_video_id(url: str) -> str | None:
    """Extract YouTube video ID from various URL formats."""
    patterns = [
        r"(?:v=|youtu\.be/)([A-Za-z0-9_-]{11})",
        r"(?:embed/)([A-Za-z0-9_-]{11})",
        r"(?:shorts/)([A-Za-z0-9_-]{11})",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def get_transcript(video_id: str) -> str:
    """Fetch transcript text for a YouTube video."""
    try:
        from youtube_transcript_api import YouTubeTranscriptApi

        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join(entry["text"] for entry in transcript)
    except Exception as exc:
        raise ValueError(f"Could not fetch transcript: {exc}") from exc


def fake_response(url: str) -> dict:
    return {
        "summary": (
            "This is a sample summary of the YouTube video. In a real session the app fetches "
            "the video transcript and asks the AI to summarize it along with key takeaways. "
            "Add an OPENAI_API_KEY to your .env file to enable real summarization."
        ),
        "key_points": [
            "The video introduces the main topic clearly.",
            "Several practical examples are demonstrated.",
            "The presenter shares actionable tips for beginners.",
            "Resources and next steps are mentioned at the end.",
        ],
        "demo": True,
    }


@app.route("/")
def index():
    return render_template("index.html", demo_mode=DEMO_MODE)


@app.route("/api/summarize", methods=["POST"])
def api_summarize():
    data = request.get_json() or {}
    url = (data.get("url") or "").strip()

    if not url:
        return jsonify({"error": "url is required"}), 400

    if DEMO_MODE:
        return jsonify(fake_response(url))

    video_id = extract_video_id(url)
    if not video_id:
        return jsonify({"error": "Could not extract video ID from the URL. Please provide a valid YouTube link."}), 400

    try:
        transcript = get_transcript(video_id)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    # Truncate to ~12 000 chars
    context = transcript[:12000]

    prompt = (
        "You are an expert content summarizer. Summarize the following YouTube video transcript "
        "and extract the key points.\n\n"
        f"Transcript:\n{context}\n\n"
        "Respond ONLY with a JSON object (no markdown fences):\n"
        '{"summary": "<2-3 paragraph summary>", "key_points": ["point1", "point2", "point3", "point4", "point5"]}'
    )

    try:
        client = get_client()
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert summarizer. Always respond with valid JSON only."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.4,
        )
    except Exception:
        result = fake_response(url)
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
    app.run(debug=True, port=5009)
