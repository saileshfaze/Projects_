const form = document.getElementById("gen-form");
const genBtn = document.getElementById("gen-btn");
const errorEl = document.getElementById("error");
const resultEl = document.getElementById("result");
const replyContent = document.getElementById("reply-content");
const copyBtn = document.getElementById("copy-btn");
const demoBadge = document.getElementById("demo-badge");

form.addEventListener("submit", async (e) => {
  e.preventDefault();

  const email_text = document.getElementById("email-text").value.trim();
  const tone = document.getElementById("tone").value;

  if (!email_text) return;

  setLoading(true);
  hideError();
  resultEl.classList.add("hidden");

  try {
    const res = await fetch("/api/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email_text, tone }),
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

function renderResult({ reply, demo }) {
  replyContent.textContent = reply || "";
  demoBadge.classList.toggle("hidden", !demo);
  resultEl.classList.remove("hidden");
  resultEl.scrollIntoView({ behavior: "smooth", block: "start" });
}

copyBtn.addEventListener("click", () => {
  navigator.clipboard.writeText(replyContent.textContent).then(() => {
    copyBtn.textContent = "Copied!";
    setTimeout(() => (copyBtn.textContent = "Copy"), 2000);
  });
});

function setLoading(loading) {
  if (loading) {
    genBtn.disabled = true;
    genBtn.innerHTML = '<span class="spinner"></span>Generating…';
  } else {
    genBtn.disabled = false;
    genBtn.textContent = "Generate Reply";
  }
}

function showError(msg) {
  errorEl.textContent = msg;
  errorEl.classList.remove("hidden");
}

function hideError() {
  errorEl.classList.add("hidden");
}
