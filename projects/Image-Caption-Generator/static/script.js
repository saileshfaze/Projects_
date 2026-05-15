const form = document.getElementById("cap-form");
const capBtn = document.getElementById("cap-btn");
const errorEl = document.getElementById("error");
const resultEl = document.getElementById("result");
const mainCaption = document.getElementById("main-caption");
const socialCaptions = document.getElementById("social-captions");
const demoBadge = document.getElementById("demo-badge");
const imageInput = document.getElementById("image");
const previewWrap = document.getElementById("preview-wrap");
const previewImg = document.getElementById("preview");

imageInput.addEventListener("change", () => {
  const file = imageInput.files[0];
  if (file) {
    previewImg.src = URL.createObjectURL(file);
    previewWrap.classList.remove("hidden");
  } else {
    previewWrap.classList.add("hidden");
  }
});

form.addEventListener("submit", async (e) => {
  e.preventDefault();

  setLoading(true);
  hideError();
  resultEl.classList.add("hidden");

  const formData = new FormData();
  if (imageInput.files[0]) {
    formData.append("image", imageInput.files[0]);
  }

  try {
    const res = await fetch("/api/caption", {
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

function renderResult({ caption, social_captions, demo }) {
  mainCaption.textContent = caption || "";

  socialCaptions.innerHTML = "";
  (social_captions || []).forEach((c) => {
    const li = document.createElement("li");
    li.textContent = c;
    socialCaptions.appendChild(li);
  });

  demoBadge.classList.toggle("hidden", !demo);
  resultEl.classList.remove("hidden");
  resultEl.scrollIntoView({ behavior: "smooth", block: "start" });
}

function setLoading(loading) {
  if (loading) {
    capBtn.disabled = true;
    capBtn.innerHTML = '<span class="spinner"></span>Analyzing…';
  } else {
    capBtn.disabled = false;
    capBtn.textContent = "Generate Captions";
  }
}

function showError(msg) {
  errorEl.textContent = msg;
  errorEl.classList.remove("hidden");
}

function hideError() {
  errorEl.classList.add("hidden");
}
