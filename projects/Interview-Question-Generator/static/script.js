const form = document.getElementById("gen-form");
const genBtn = document.getElementById("gen-btn");
const errorEl = document.getElementById("error");
const resultEl = document.getElementById("result");
const questionsList = document.getElementById("questions-list");
const demoBadge = document.getElementById("demo-badge");

form.addEventListener("submit", async (e) => {
  e.preventDefault();

  const topic = document.getElementById("topic").value.trim();
  const level = document.getElementById("level").value;
  const count = parseInt(document.getElementById("count").value, 10);

  if (!topic) return;

  setLoading(true);
  hideError();
  resultEl.classList.add("hidden");

  try {
    const res = await fetch("/api/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ topic, level, count }),
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

function renderResult({ questions, demo }) {
  questionsList.innerHTML = "";

  (questions || []).forEach((item, index) => {
    const li = document.createElement("li");
    li.innerHTML = `
      <div class="q-card">
        <div class="q-header" data-open="false">
          <span class="q-num">${index + 1}</span>
          <span style="flex:1">${escapeHtml(item.question)}</span>
          <span class="q-toggle">&#43;</span>
        </div>
        <div class="q-answer hidden">${escapeHtml(item.answer)}</div>
      </div>
    `;

    const header = li.querySelector(".q-header");
    const answer = li.querySelector(".q-answer");
    const toggle = li.querySelector(".q-toggle");

    header.addEventListener("click", () => {
      const isOpen = header.dataset.open === "true";
      answer.classList.toggle("hidden", isOpen);
      toggle.innerHTML = isOpen ? "&#43;" : "&#8722;";
      header.dataset.open = String(!isOpen);
    });

    questionsList.appendChild(li);
  });

  demoBadge.classList.toggle("hidden", !demo);
  resultEl.classList.remove("hidden");
  resultEl.scrollIntoView({ behavior: "smooth", block: "start" });
}

function escapeHtml(str) {
  return (str || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function setLoading(loading) {
  if (loading) {
    genBtn.disabled = true;
    genBtn.innerHTML = '<span class="spinner"></span>Generating…';
  } else {
    genBtn.disabled = false;
    genBtn.textContent = "Generate Questions";
  }
}

function showError(msg) {
  errorEl.textContent = msg;
  errorEl.classList.remove("hidden");
}

function hideError() {
  errorEl.classList.add("hidden");
}
