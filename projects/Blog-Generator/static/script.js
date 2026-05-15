const form = document.getElementById("gen-form");
const genBtn = document.getElementById("gen-btn");
const errorEl = document.getElementById("error");
const resultEl = document.getElementById("result");
const blogTitle = document.getElementById("blog-title");
const blogContent = document.getElementById("blog-content");
const keywordsList = document.getElementById("keywords");
const copyBtn = document.getElementById("copy-btn");
const demoBadge = document.getElementById("demo-badge");

form.addEventListener("submit", async (e) => {
  e.preventDefault();

  const topic = document.getElementById("topic").value.trim();
  const tone = document.getElementById("tone").value;

  if (!topic) return;

  setLoading(true);
  hideError();
  resultEl.classList.add("hidden");

  try {
    const res = await fetch("/api/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ topic, tone }),
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

function renderResult({ title, content, seo_keywords, demo }) {
  blogTitle.textContent = title || "";
  blogContent.textContent = content || "";

  keywordsList.innerHTML = "";
  (seo_keywords || []).forEach((kw) => {
    const li = document.createElement("li");
    li.textContent = kw;
    keywordsList.appendChild(li);
  });

  demoBadge.classList.toggle("hidden", !demo);

  resultEl.classList.remove("hidden");
  resultEl.scrollIntoView({ behavior: "smooth", block: "start" });
}

copyBtn.addEventListener("click", () => {
  const text = `${blogTitle.textContent}\n\n${blogContent.textContent}`;
  navigator.clipboard.writeText(text).then(() => {
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
    genBtn.textContent = "Generate Blog Post";
  }
}

function showError(msg) {
  errorEl.textContent = msg;
  errorEl.classList.remove("hidden");
}

function hideError() {
  errorEl.classList.add("hidden");
}
