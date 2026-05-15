import io
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


def get_client():
    global _client
    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set.")
        _client = OpenAI(api_key=api_key)
    return _client


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract plain text from PDF bytes using PyPDF2."""
    try:
        import PyPDF2

        reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n\n".join(pages).strip()
    except Exception as exc:
        raise ValueError(f"Could not read PDF: {exc}") from exc


def fake_response(question: str) -> dict:
    """Return sample answer when no API key is configured."""
    return {
        "answer": (
            f"This is a sample answer for the question: \"{question}\"\n\n"
            "In a real session the app reads your PDF, extracts the text, "
            "and asks the AI to find the answer within that content. "
            "Add an OPENAI_API_KEY to your .env file to enable real answers."
        ),
        "demo": True,
    }


@app.route("/")
def index():
    return render_template("index.html", demo_mode=DEMO_MODE)


@app.route("/api/ask", methods=["POST"])
def api_ask():
    question = (request.form.get("question") or "").strip()
    pdf_file = request.files.get("pdf")

    if not question:
        return jsonify({"error": "question is required"}), 400

    if DEMO_MODE:
        return jsonify(fake_response(question))

    if not pdf_file:
        return jsonify({"error": "pdf file is required"}), 400

    try:
        pdf_text = extract_text_from_pdf(pdf_file.read())
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    if not pdf_text:
        return jsonify({"error": "Could not extract text from the PDF. It may be image-based."}), 400

    # Truncate to ~12 000 chars to stay within token limits
    context = pdf_text[:12000]

    prompt = (
        "You are a helpful assistant that answers questions based solely on the provided document.\n\n"
        f"Document:\n{context}\n\n"
        f"Question: {question}\n\n"
        "Respond ONLY with a JSON object (no markdown fences):\n"
        '{"answer": "<your answer based on the document>"}'
    )

    try:
        client = get_client()
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You answer questions based on document content. Always respond with valid JSON only."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
        )
    except Exception:
        result = fake_response(question)
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
    app.run(debug=True, port=5007)
