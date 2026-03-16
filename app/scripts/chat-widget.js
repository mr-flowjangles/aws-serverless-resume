/**
 * RobbAI Chat Widget
 * Floating chat bubble that connects to Bot Factory streaming endpoint.
 */

const CHAT_CONFIG = {
  apiUrl: 'https://4bu5vwwizdql4wzwh6dqhke62m0oyrbk.lambda-url.us-east-1.on.aws',
  botId: 'RobbAI',
  apiKey: 'bfk_WwXLDR2X8OcvNnt4Nc50aPD7ghSd5QMCIt9Gimfrejo',
  suggestions: [
    'What does Rob do?',
    "Tell me about Rob's projects",
    'What tech does Rob work with?',
    "What are Rob's hobbies?",
  ],
};

function initChatWidget() {
  // Build DOM
  const bubble = document.createElement('button');
  bubble.className = 'chat-bubble';
  bubble.setAttribute('aria-label', 'Open chat');
  bubble.textContent = '\u{1F4AC}';

  const panel = document.createElement('div');
  panel.className = 'chat-panel';
  panel.innerHTML = `
    <div class="chat-panel-header">
      <span class="chat-title"><span class="dot"></span> RobbAI</span>
      <button class="chat-panel-close" aria-label="Close chat">&times;</button>
    </div>
    <div class="chat-messages" id="chatMessages">
      <div class="chat-msg bot">Hey! I'm RobbAI, Rob's AI assistant. Ask me anything about his experience, projects, or skills.</div>
    </div>
    <div class="chat-suggestions" id="chatSuggestions"></div>
    <div class="chat-input-area">
      <textarea class="chat-input" id="chatInput" placeholder="Ask something..." rows="1"></textarea>
      <button class="chat-send" id="chatSend">Send</button>
    </div>
  `;

  document.body.appendChild(bubble);
  document.body.appendChild(panel);

  // Elements
  const messages = document.getElementById('chatMessages');
  const input = document.getElementById('chatInput');
  const sendBtn = document.getElementById('chatSend');
  const suggestionsEl = document.getElementById('chatSuggestions');
  const closeBtn = panel.querySelector('.chat-panel-close');

  // Render suggestions
  function renderSuggestions() {
    suggestionsEl.innerHTML = '';
    CHAT_CONFIG.suggestions.forEach((text) => {
      const btn = document.createElement('button');
      btn.className = 'chat-suggestion';
      btn.textContent = text;
      btn.addEventListener('click', () => sendMessage(text));
      suggestionsEl.appendChild(btn);
    });
  }

  renderSuggestions();

  // Toggle
  bubble.addEventListener('click', () => {
    panel.classList.add('open');
    bubble.classList.add('hidden');
    input.focus();
  });

  closeBtn.addEventListener('click', () => {
    panel.classList.remove('open');
    bubble.classList.remove('hidden');
  });

  // Input handling
  input.addEventListener('input', () => {
    input.style.height = 'auto';
    input.style.height = Math.min(input.scrollHeight, 100) + 'px';
  });

  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage(input.value);
    }
  });

  sendBtn.addEventListener('click', () => sendMessage(input.value));

  function addMessage(text, role) {
    const div = document.createElement('div');
    div.className = 'chat-msg ' + role;
    div.textContent = text;
    messages.appendChild(div);
    messages.scrollTop = messages.scrollHeight;
    return div;
  }

  function showTyping() {
    const div = document.createElement('div');
    div.className = 'chat-typing';
    div.id = 'chatTyping';
    div.innerHTML = '<span></span><span></span><span></span>';
    messages.appendChild(div);
    messages.scrollTop = messages.scrollHeight;
  }

  function hideTyping() {
    const el = document.getElementById('chatTyping');
    if (el) el.remove();
  }

  async function sendMessage(text) {
    text = text.trim();
    if (!text) return;

    addMessage(text, 'user');
    input.value = '';
    input.style.height = 'auto';
    sendBtn.disabled = true;

    // Hide suggestions after first message
    suggestionsEl.style.display = 'none';

    showTyping();

    try {
      const res = await fetch(CHAT_CONFIG.apiUrl + '/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': CHAT_CONFIG.apiKey,
        },
        body: JSON.stringify({ bot_id: CHAT_CONFIG.botId, message: text }),
      });

      if (!res.ok) {
        hideTyping();
        let errMsg = res.statusText;
        try {
          const err = await res.json();
          errMsg = err.error || errMsg;
        } catch {}
        addMessage('Sorry, something went wrong. Try again later.', 'bot');
        sendBtn.disabled = false;
        input.focus();
        return;
      }

      hideTyping();
      const botDiv = addMessage('', 'bot');

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';
      let fullText = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop();

        for (const line of lines) {
          if (!line.startsWith('data: ')) continue;
          const payload = line.slice(6).trim();
          if (payload === '[DONE]') continue;

          try {
            const data = JSON.parse(payload);
            if (data.error) {
              fullText += 'Sorry, something went wrong.';
            } else if (data.token) {
              fullText += data.token;
            }
            // Skip sources — not shown in production widget
            botDiv.textContent = fullText;
            messages.scrollTop = messages.scrollHeight;
          } catch {}
        }
      }
    } catch {
      hideTyping();
      addMessage("Couldn't reach the server. Please try again later.", 'bot');
    }

    sendBtn.disabled = false;
    input.focus();
  }
}

// Init when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initChatWidget);
} else {
  initChatWidget();
}
