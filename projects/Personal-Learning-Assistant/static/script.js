const form = document.getElementById("learn-form");
const learnBtn = document.getElementById("learn-btn");
const errorEl = document.getElementById("error");
const resultEl = document.getElementById("result");
const explanationEl = document.getElementById("explanation");
const practiceList = document.getElementById("practice-list");
const nextList = document.getElementById("next-list");
const demoBadge = document.getElementById("demo-badge");

form.addEventListener("submit", async (e) => {
  e.preventDefault();

  const question = document.getElementById("question").value.trim();
  const level = document.getElementById("level").value;

  if (!question) return;

  setLoading(true);
  hideError();
  resultEl.classList.add("hidden");

  try {
    const res = await fetch("/api/learn", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question, level }),
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

function renderResult({ explanation, practice_questions, next_topics, demo }) {
  explanationEl.textContent = explanation || "";

  practiceList.innerHTML = "";
  (practice_questions || []).forEach((q) => {
    const li = document.createElement("li");
    li.textContent = q;
    practiceList.appendChild(li);
  });

  nextList.innerHTML = "";
  (next_topics || []).forEach((t) => {
    const li = document.createElement("li");
    li.textContent = t;
    nextList.appendChild(li);
  });

  demoBadge.classList.toggle("hidden", !demo);
  resultEl.classList.remove("hidden");
  resultEl.scrollIntoView({ behavior: "smooth", block: "start" });
}

function setLoading(loading) {
  if (loading) {
    learnBtn.disabled = true;
    learnBtn.innerHTML = '<span class="spinner"></span>Thinking…';
  } else {
    learnBtn.disabled = false;
    learnBtn.textContent = "Ask Tutor";
  }
}

function showError(msg) {
  errorEl.textContent = msg;
  errorEl.classList.remove("hidden");
}

function hideError() {
  errorEl.classList.add("hidden");
}
