// File drag-and-drop label update
const fileDrop = document.getElementById("file-drop");
const fileInput = document.getElementById("resume");
const fileLabel = document.getElementById("file-label");

fileInput.addEventListener("change", () => {
  fileLabel.textContent = fileInput.files[0]
    ? fileInput.files[0].name
    : "Click to choose a file or drag & drop here";
});

fileDrop.addEventListener("dragover", (e) => {
  e.preventDefault();
  fileDrop.classList.add("drag-over");
});

fileDrop.addEventListener("dragleave", () =>
  fileDrop.classList.remove("drag-over"),
);

fileDrop.addEventListener("drop", (e) => {
  e.preventDefault();
  fileDrop.classList.remove("drag-over");
  if (e.dataTransfer.files.length) {
    fileInput.files = e.dataTransfer.files;
    fileLabel.textContent = fileInput.files[0].name;
  }
});

// Form submission
document
  .getElementById("analyze-form")
  .addEventListener("submit", async (e) => {
    e.preventDefault();

    const btn = document.getElementById("submit-btn");
    const errorBox = document.getElementById("error-box");
    const results = document.getElementById("results");

    errorBox.classList.add("hidden");
    results.classList.add("hidden");
    btn.disabled = true;
    btn.textContent = "Analyzing…";

    const formData = new FormData(e.target);

    try {
      const res = await fetch("/api/analyze", {
        method: "POST",
        body: formData,
      });
      const data = await res.json();

      if (!res.ok || data.error) {
        showError(data.error || "An unexpected error occurred.");
        return;
      }

      renderResults(data);
    } catch {
      showError("Network error — please try again.");
    } finally {
      btn.disabled = false;
      btn.textContent = "Analyze";
    }
  });

function showError(msg) {
  const box = document.getElementById("error-box");
  box.textContent = msg;
  box.classList.remove("hidden");
}

function renderResults(data) {
  document.getElementById("summary-text").textContent = data.summary || "—";

  renderList("gaps-list", data.skill_gaps);
  renderList("suggestions-list", data.suggestions);

  document.getElementById("results").classList.remove("hidden");
  document.getElementById("results").scrollIntoView({ behavior: "smooth" });
}

function renderList(id, items) {
  const ul = document.getElementById(id);
  ul.innerHTML = "";
  const list = Array.isArray(items) ? items : [];
  if (!list.length) {
    const li = document.createElement("li");
    li.textContent = "None provided.";
    ul.appendChild(li);
    return;
  }
  list.forEach((item) => {
    const li = document.createElement("li");
    li.textContent = item;
    ul.appendChild(li);
  });
}
