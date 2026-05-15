async function fetchHistory() {
  const res = await fetch("/api/history");
  return res.ok ? res.json() : [];
}

function renderMessages(messages) {
  const chat = document.getElementById("chat");
  chat.innerHTML = "";
  messages.forEach((m) => {
    const el = document.createElement("div");
    el.className = "message " + (m.role === "user" ? "user" : "assistant");
    el.textContent = (m.role === "user" ? "You: " : "AI: ") + m.content;
    chat.appendChild(el);
  });
  chat.scrollTop = chat.scrollHeight;
}

document.getElementById("chat-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const input = document.getElementById("message");
  const text = input.value.trim();
  if (!text) return;
  input.value = "";

  // Optimistic UI: append user message
  const cur = await fetchHistory();
  renderMessages([...cur, { role: "user", content: text }]);

  const res = await fetch("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: text }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ error: "Unknown error" }));
    alert("Error: " + (err.error || "Failed to get reply"));
    return;
  }
  const data = await res.json();
  const newHistory = await fetchHistory();
  renderMessages(newHistory);
});

// Load history on start
fetchHistory()
  .then(renderMessages)
  .catch(() => {});
