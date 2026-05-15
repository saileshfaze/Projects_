import base64
import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from openai import OpenAI

load_dotenv(Path(__file__).parent / ".env")

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10 MB limit

_client = None
DEMO_MODE = not os.getenv("OPENAI_API_KEY")

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def get_client():
    global _client
    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set.")
        _client = OpenAI(api_key=api_key)
    return _client


def fake_response() -> dict:
    return {
        "caption": "A vibrant scene captured in stunning detail, showcasing the beauty of everyday life.",
        "social_captions": [
            "Living in the moment ✨ #photography #life",
            "Every picture tells a story 📸 #photooftheday",
            "The world through my lens 🌍 #explore #capture",
        ],
        "demo": True,
    }


@app.route("/")
def index():
    return render_template("index.html", demo_mode=DEMO_MODE)


@app.route("/api/caption", methods=["POST"])
def api_caption():
    if DEMO_MODE:
        return jsonify(fake_response())

    image_file = request.files.get("image")
    if not image_file:
        return jsonify({"error": "image file is required"}), 400

    if not allowed_file(image_file.filename or ""):
        return jsonify({"error": "Unsupported file type. Use PNG, JPG, JPEG, GIF, or WEBP."}), 400

    image_bytes = image_file.read()
    ext = (image_file.filename or "image.jpg").rsplit(".", 1)[-1].lower()
    mime = f"image/{'jpeg' if ext in ('jpg', 'jpeg') else ext}"
    b64 = base64.b64encode(image_bytes).decode("utf-8")
    data_url = f"data:{mime};base64,{b64}"

    prompt = (
        "Describe this image in one clear, engaging sentence as a caption. "
        "Then provide 3 creative social media captions with relevant hashtags.\n\n"
        "Respond ONLY with a JSON object (no markdown fences):\n"
        '{"caption": "<main caption>", "social_captions": ["caption1", "caption2", "caption3"]}'
    )

    try:
        client = get_client()
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": data_url}},
                        {"type": "text", "text": prompt},
                    ],
                }
            ],
            temperature=0.7,
        )
    except Exception:
        result = fake_response()
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
    app.run(debug=True, port=5005)
