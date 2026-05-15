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


def fake_response(email_text: str, tone: str) -> dict:
    """Return sample reply when no API key is configured."""
    greeting = "Dear Sender," if tone == "formal" else "Hey,"
    closing = "Best regards,\n[Your Name]" if tone == "formal" else "Cheers,\n[Your Name]"
    reply = (
        f"{greeting}\n\n"
        f"Thank you for reaching out. I have reviewed your message carefully and "
        f"I am happy to provide a {'formal' if tone == 'formal' else 'friendly'} response.\n\n"
        f"Regarding your inquiry, I would like to confirm that we will look into this matter "
        f"and get back to you with a comprehensive answer as soon as possible.\n\n"
        f"Please do not hesitate to contact us if you need any further assistance.\n\n"
        f"{closing}"
    )
    return {"reply": reply, "demo": True}


@app.route("/")
def index():
    return render_template("index.html", demo_mode=DEMO_MODE)


@app.route("/api/generate", methods=["POST"])
def api_generate():
    data = request.get_json() or {}
    email_text = (data.get("email_text") or "").strip()
    tone = (data.get("tone") or "formal").strip()

    if not email_text:
        return jsonify({"error": "email_text is required"}), 400

    if DEMO_MODE:
        return jsonify(fake_response(email_text, tone))

    prompt = (
        f"You are an expert email writer. Write a {tone} reply to the following email:\n\n"
        f"---\n{email_text}\n---\n\n"
        "Respond ONLY with a JSON object (no markdown fences):\n"
        '{"reply": "<the full email reply>"}'
    )

    try:
        client = get_client()
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert email writer. Always respond with valid JSON only."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.6,
        )
    except Exception:
        result = fake_response(email_text, tone)
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
    app.run(debug=True, port=5004)
