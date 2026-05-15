import io
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from openai import OpenAI

load_dotenv(Path(__file__).parent / ".env")

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB upload limit

_client = None
DEMO_MODE = not os.getenv("OPENAI_API_KEY")

ALLOWED_EXTENSIONS = {"pdf", "txt", "docx"}


def get_client():
    global _client
    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set.")
        _client = OpenAI(api_key=api_key)
    return _client


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def extract_text(file) -> str:
    """Extract plain text from an uploaded PDF, DOCX, or TXT file."""
    ext = file.filename.rsplit(".", 1)[1].lower()
    data = file.read()

    if ext == "pdf":
        import PyPDF2

        reader = PyPDF2.PdfReader(io.BytesIO(data))
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(pages).strip()

    if ext == "docx":
        import docx

        doc = docx.Document(io.BytesIO(data))
        return "\n".join(p.text for p in doc.paragraphs).strip()

    # Plain text
    return data.decode("utf-8", errors="replace").strip()


def fake_response() -> dict:
    """Return sample analysis when no API key is configured."""
    return {
        "summary": (
            "The candidate has a solid background in software development with experience in "
            "Python, web frameworks, and database management. Their profile shows strong "
            "technical foundations and a track record of delivering projects on time. "
            "Overall fit for the role appears promising based on the submitted resume."
        ),
        "skill_gaps": [
            "Cloud infrastructure experience (AWS/GCP/Azure) not mentioned",
            "No evidence of CI/CD pipeline configuration",
            "Limited experience with containerization (Docker/Kubernetes)",
        ],
        "suggestions": [
            "Quantify your achievements — add metrics like '20% performance improvement'.",
            "Include relevant certifications (e.g., AWS Certified Developer).",
            "Add a 'Projects' section with links to GitHub repositories.",
            "Tailor the summary to match keywords from the job description.",
        ],
        "demo": True,
    }


@app.route("/")
def index():
    return render_template("index.html", demo_mode=DEMO_MODE)


@app.route("/api/analyze", methods=["POST"])
def api_analyze():
    if DEMO_MODE:
        return jsonify(fake_response())

    if "resume" not in request.files:
        return jsonify({"error": "No resume file uploaded."}), 400

    resume_file = request.files["resume"]
    if not resume_file.filename or not allowed_file(resume_file.filename):
        return jsonify({"error": "Unsupported file type. Upload a PDF, DOCX, or TXT."}), 400

    job_description = (request.form.get("job_description") or "").strip()
    if not job_description:
        return jsonify({"error": "Job description is required."}), 400

    try:
        resume_text = extract_text(resume_file)
    except Exception as e:
        return jsonify({"error": f"Failed to read file: {e}"}), 400

    if not resume_text:
        return jsonify({"error": "Could not extract text from the resume."}), 400

    prompt = f"""You are a professional resume coach and hiring expert.
Analyze the resume below against the provided job description.

RESUME:
{resume_text[:4000]}

JOB DESCRIPTION:
{job_description[:2000]}

Respond with a JSON object containing exactly these three keys:
- "summary": string — 3-5 sentences summarising the candidate's profile and overall fit.
- "skill_gaps": array of strings — 3-6 skills or areas the candidate is missing or should strengthen for this role.
- "suggestions": array of strings — 3-6 specific, actionable improvements to make the resume stronger for this role.

Return only valid JSON with no markdown fencing."""

    try:
        resp = get_client().chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=900,
            temperature=0.3,
        )
        content = resp.choices[0].message.content.strip()
        # Strip markdown code fences if present
        if content.startswith("```"):
            parts = content.split("```")
            content = parts[1].lstrip("json").strip() if len(parts) > 1 else content
        result = json.loads(content)
    except json.JSONDecodeError:
        return jsonify({"error": "Model returned non-JSON response. Please try again."}), 500
    except Exception:
        result = fake_response()
        return jsonify(result)

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True, port=5001)
