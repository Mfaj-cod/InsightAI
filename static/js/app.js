document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("chat-form");
  const chatBox = document.getElementById("chat-box");

  if (form) {
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const queryInput = document.getElementById("query");
      const query = queryInput.value;

      if (!query) return;

      // User message bubble
      const userBubble = document.createElement("div");
      userBubble.className = "chat-message user";
      userBubble.textContent = query;
      chatBox.appendChild(userBubble);
      chatBox.scrollTop = chatBox.scrollHeight;
      queryInput.value = "";

      // Send query to Flask
      const res = await fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: `query=${encodeURIComponent(query)}`
      });

      const data = await res.json();

      // Bot message bubble
      const botBubble = document.createElement("div");
      botBubble.className = "chat-message bot";
      botBubble.textContent = data.answer;
      chatBox.appendChild(botBubble);
      chatBox.scrollTop = chatBox.scrollHeight;
    });
  }
});
