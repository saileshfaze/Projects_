const form = document.getElementById("sum-form");
const sumBtn = document.getElementById("sum-btn");
const errorEl = document.getElementById("error");
const resultEl = document.getElementById("result");
const summaryText = document.getElementById("summary-text");
const keyPoints = document.getElementById("key-points");
const copyBtn = document.getElementById("copy-btn");
const demoBadge = document.getElementById("demo-badge");

form.addEventListener("submit", async (e) => {
  e.preventDefault();

  const url = document.getElementById("url").value.trim();
  if (!url) return;

  setLoading(true);
  hideError();
  resultEl.classList.add("hidden");

  try {
    const res = await fetch("/api/summarize", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url }),
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

function renderResult({ summary, key_points, demo }) {
  summaryText.textContent = summary || "";

  keyPoints.innerHTML = "";
  (key_points || []).forEach((pt) => {
    const li = document.createElement("li");
    li.textContent = pt;
    keyPoints.appendChild(li);
  });

  demoBadge.classList.toggle("hidden", !demo);
  resultEl.classList.remove("hidden");
  resultEl.scrollIntoView({ behavior: "smooth", block: "start" });
}

copyBtn.addEventListener("click", () => {
  const points = Array.from(keyPoints.querySelectorAll("li"))
    .map((li) => `• ${li.textContent}`)
    .join("\n");
  const text = `${summaryText.textContent}\n\nKey Points:\n${points}`;
  navigator.clipboard.writeText(text).then(() => {
    copyBtn.textContent = "Copied!";
    setTimeout(() => (copyBtn.textContent = "Copy"), 2000);
  });
});

function setLoading(loading) {
  if (loading) {
    sumBtn.disabled = true;
    sumBtn.innerHTML = '<span class="spinner"></span>Summarizing…';
  } else {
    sumBtn.disabled = false;
    sumBtn.textContent = "Summarize";
  }
}

function showError(msg) {
  errorEl.textContent = msg;
  errorEl.classList.remove("hidden");
}

function hideError() {
  errorEl.classList.add("hidden");
}
