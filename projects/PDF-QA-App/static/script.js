const form = document.getElementById("qa-form");
const askBtn = document.getElementById("ask-btn");
const errorEl = document.getElementById("error");
const resultEl = document.getElementById("result");
const answerContent = document.getElementById("answer-content");
const copyBtn = document.getElementById("copy-btn");
const demoBadge = document.getElementById("demo-badge");

form.addEventListener("submit", async (e) => {
  e.preventDefault();

  const question = document.getElementById("question").value.trim();
  const pdfInput = document.getElementById("pdf");

  if (!question) return;

  setLoading(true);
  hideError();
  resultEl.classList.add("hidden");

  const formData = new FormData();
  formData.append("question", question);
  if (pdfInput.files[0]) {
    formData.append("pdf", pdfInput.files[0]);
  }

  try {
    const res = await fetch("/api/ask", {
      method: "POST",
      body: formData,
    });

    const data = await res.json();

    if (!res.ok) {
      showError(data.error || "Something went wrong. Please try again.");
      return;
    }

    renderResult(data);
  } catch (err) {
    showError("Network error. Is the server running?");
  } finally {
    setLoading(false);
  }
});

function renderResult({ answer, demo }) {
  answerContent.textContent = answer || "";
  demoBadge.classList.toggle("hidden", !demo);
  resultEl.classList.remove("hidden");
  resultEl.scrollIntoView({ behavior: "smooth", block: "start" });
}

copyBtn.addEventListener("click", () => {
  navigator.clipboard.writeText(answerContent.textContent).then(() => {
    copyBtn.textContent = "Copied!";
    setTimeout(() => (copyBtn.textContent = "Copy"), 2000);
  });
});

function setLoading(loading) {
  if (loading) {
    askBtn.disabled = true;
    askBtn.innerHTML = '<span class="spinner"></span>Thinking…';
  } else {
    askBtn.disabled = false;
    askBtn.textContent = "Ask Question";
  }
}

function showError(msg) {
  errorEl.textContent = msg;
  errorEl.classList.remove("hidden");
}

function hideError() {
  errorEl.classList.add("hidden");
}
