const form = document.getElementById("code-form");
const explainBtn = document.getElementById("explain-btn");
const errorEl = document.getElementById("error");
const resultEl = document.getElementById("result");
const summaryText = document.getElementById("summary-text");
const bugsList = document.getElementById("bugs-list");
const optsList = document.getElementById("opts-list");
const demoBadge = document.getElementById("demo-badge");

form.addEventListener("submit", async (e) => {
  e.preventDefault();

  const code = document.getElementById("code").value.trim();
  const language = document.getElementById("language").value;

  if (!code) return;

  setLoading(true);
  hideError();
  resultEl.classList.add("hidden");

  try {
    const res = await fetch("/api/explain", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ code, language }),
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

function renderResult({ summary, bugs, optimizations, demo }) {
  summaryText.textContent = summary || "";

  renderList(bugsList, bugs || []);
  renderList(optsList, optimizations || []);

  demoBadge.classList.toggle("hidden", !demo);
  resultEl.classList.remove("hidden");
  resultEl.scrollIntoView({ behavior: "smooth", block: "start" });
}

function renderList(el, items) {
  el.innerHTML = "";
  if (!items.length) {
    const li = document.createElement("li");
    li.textContent = "None identified.";
    el.appendChild(li);
    return;
  }
  items.forEach((item) => {
    const li = document.createElement("li");
    li.textContent = item;
    el.appendChild(li);
  });
}

function setLoading(loading) {
  if (loading) {
    explainBtn.disabled = true;
    explainBtn.innerHTML = '<span class="spinner"></span>Analyzing…';
  } else {
    explainBtn.disabled = false;
    explainBtn.textContent = "Explain Code";
  }
}

function showError(msg) {
  errorEl.textContent = msg;
  errorEl.classList.remove("hidden");
}

function hideError() {
  errorEl.classList.add("hidden");
}
