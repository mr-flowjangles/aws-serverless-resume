/**
 * Bot Factory — Chat Module
 *
 * Handles chat messaging, typing indicators, and suggestion chips.
 * Configurable via BOT_CONFIG object set in the HTML page.
 *
 * Required: Set window.BOT_CONFIG before loading this script.
 *   window.BOT_CONFIG = {
 *     apiUrl: '/api/guitar',
 *     botName: 'The Fret Detective',
 *     placeholder: 'Ask about guitar...'
 *   };
 *
 * Optional: Set window.BOT_CONFIG.formatMessage to a function that
 * takes (text, containerDiv) and handles custom rendering.
 * If not set, messages render as plain text.
 */

const chatMessages = document.getElementById("chatMessages");
const chatInput = document.getElementById("chatInput");
const chatSuggestions = document.getElementById("chatSuggestions");

const config = window.BOT_CONFIG || {
  apiUrl: "/api/bot",
  botName: "Bot",
  placeholder: "Type a message...",
};

// Conversation history — persists for the browser session.
// Resets on page refresh, which is fine for a casual chatbot.
const conversationHistory = [];

/**
 * Send a suggestion chip's text as a message
 */
function sendSuggestion(chip) {
  chatInput.value = chip.textContent;
  sendMessage();
}

/**
 * Send the current input as a message
 */
/**
 * Send the current input as a message (with streaming)
 */
async function sendMessage() {
  const message = chatInput.value.trim();
  if (!message) return;

  addMessage(message, "user");
  chatInput.value = "";

  // Hide suggestions after first message
  if (chatSuggestions) {
    chatSuggestions.style.display = "none";
  }

  const typing = showTyping();

  try {
    const response = await fetch(`${config.apiUrl}/chat/stream`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message,
        conversation_history: conversationHistory,
      }),
    });

    // Create bot message container (but don't remove typing yet)
    const div = document.createElement("div");
    div.className = "chat-message bot";
    const label = document.createElement("div");
    label.className = "bot-label";
    label.textContent = config.botName;
    div.appendChild(label);

    // Stream the response
    let fullResponse = "";
    let firstChunk = true;
    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      // Remove typing indicator on first chunk
      if (firstChunk) {
        typing.remove();
        chatMessages.appendChild(div);
        firstChunk = false;
      }

      const chunk = decoder.decode(value, { stream: true });
      fullResponse += chunk;

      // Update the message content
      while (div.childNodes.length > 1) {
        div.removeChild(div.lastChild);
      }

      const formatter = config.formatMessage || defaultFormatMessage;
      formatter(fullResponse, div);

      chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value, { stream: true });
      fullResponse += chunk;

      // Update the message content
      // Remove old text nodes (keep the label)
      while (div.childNodes.length > 1) {
        div.removeChild(div.lastChild);
      }

      // Re-render with formatter
      const formatter = config.formatMessage || defaultFormatMessage;
      formatter(fullResponse, div);

      chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Track both sides of the exchange for follow-ups
    conversationHistory.push(
      { role: "user", content: message },
      { role: "assistant", content: fullResponse },
    );

    // Cap at 10 exchanges (20 messages) to keep token costs in check
    const maxMessages = 20;
    if (conversationHistory.length > maxMessages) {
      conversationHistory.splice(0, conversationHistory.length - maxMessages);
    }
  } catch (error) {
    typing.remove();
    addMessage("Sorry, I couldn't connect. Try again in a moment.", "bot");
  }
}

/**
 * Add a message bubble to the chat
 */
function addMessage(text, type) {
  const div = document.createElement("div");
  div.className = `chat-message ${type}`;

  if (type === "bot") {
    const label = document.createElement("div");
    label.className = "bot-label";
    label.textContent = config.botName;
    div.appendChild(label);

    // Use custom formatter if registered, otherwise plain text
    const formatter = config.formatMessage || defaultFormatMessage;
    formatter(text, div);
  } else {
    div.textContent = text;
  }

  chatMessages.appendChild(div);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

/**
 * Show typing indicator, returns the element for removal
 */
function showTyping() {
  const div = document.createElement("div");
  div.className = "typing-indicator";
  div.innerHTML = "<span></span><span></span><span></span>";
  chatMessages.appendChild(div);
  chatMessages.scrollTop = chatMessages.scrollHeight;
  return div;
}

// Enter key sends message
chatInput.addEventListener("keydown", function (e) {
  if (e.key === "Enter") sendMessage();
});

// Warm up embedding cache on page load
fetch(`${config.apiUrl}/warmup`).catch(() => {});
