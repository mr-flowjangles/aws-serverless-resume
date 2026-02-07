/**
 * RobbAI Chatbot Widget
 * Loads conditionally based on backend config
 * Self-contained, no dependencies
 */

(async function() {
  'use strict';

  // API base URL
  const API_BASE = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? '/api'
    : 'https://qehzqmqmwg.execute-api.us-east-1.amazonaws.com/prod/api';

  // Check if chatbot is enabled
  let config;
  try {
    const response = await fetch(`${API_BASE}/ai/chatbot/config`);
    config = await response.json();
  } catch (error) {
    console.log('Chatbot config not available');
    return; // Exit if can't load config
  }

  // Exit if disabled
  if (!config.enabled) {
    console.log('Chatbot is disabled');
    return;
  }

  // Chatbot is enabled - initialize
  console.log(`${config.name} chatbot enabled`);

  // Create and inject styles
  const styles = `
    .robbai-widget {
      position: fixed;
      bottom: 20px;
      right: 20px;
      z-index: 10000;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
    }

    .robbai-button {
      width: 60px;
      height: 60px;
      border-radius: 50%;
      background: linear-gradient(135deg, #0284c7, #0ea5e9);
      border: none;
      color: white;
      font-size: 24px;
      cursor: pointer;
      box-shadow: 0 4px 12px rgba(2, 132, 199, 0.4);
      transition: all 0.3s ease;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .robbai-button:hover {
      transform: scale(1.1);
      box-shadow: 0 6px 16px rgba(2, 132, 199, 0.5);
    }

    .robbai-button.hidden {
      display: none;
    }

    .robbai-container {
      position: fixed;
      bottom: 90px;
      right: 20px;
      width: 400px;
      height: 600px;
      background: white;
      border-radius: 12px;
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
      display: none;
      flex-direction: column;
      overflow: hidden;
    }

    .robbai-container.open {
      display: flex;
    }

    .robbai-header {
      background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
      color: white;
      padding: 1rem 1.5rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .robbai-header h3 {
      margin: 0;
      font-size: 1.1rem;
      font-weight: 600;
    }

    .robbai-header p {
      margin: 0;
      font-size: 0.85rem;
      color: #94a3b8;
    }

    .robbai-close {
      background: none;
      border: none;
      color: white;
      font-size: 24px;
      cursor: pointer;
      padding: 0;
      width: 30px;
      height: 30px;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: transform 0.2s;
    }

    .robbai-close:hover {
      transform: scale(1.1);
    }

    .robbai-info-banner {
      background: #e0f2fe;
      color: #0369a1;
      padding: 0.5rem 1rem;
      font-size: 0.85rem;
      text-align: center;
      border-bottom: 1px solid #bae6fd;
    }

    .robbai-messages {
      flex: 1;
      overflow-y: auto;
      padding: 1rem;
      background: #f0f4f8;
      scroll-behavior: smooth;
    }

    .robbai-message {
      margin-bottom: 1rem;
      padding: 0.75rem 1rem;
      border-radius: 8px;
      max-width: 85%;
      line-height: 1.5;
      font-size: 0.95rem;
    }

    .robbai-message.user {
      background: #0284c7;
      color: white;
      margin-left: auto;
    }

    .robbai-message.assistant {
      background: white;
      color: #0f172a;
      border-left: 4px solid #0284c7;
      box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
    }

    .robbai-message.assistant .name {
      font-weight: 600;
      color: #0284c7;
      margin-bottom: 0.3rem;
      font-size: 0.8rem;
    }

    .robbai-message.loading {
      color: #64748b;
      font-style: italic;
    }

    .robbai-input-area {
      padding: 1rem;
      background: white;
      border-top: 1px solid #e2e8f0;
      display: flex;
      gap: 0.5rem;
    }

    .robbai-input-area input {
      flex: 1;
      padding: 0.75rem;
      border: 2px solid #e2e8f0;
      border-radius: 8px;
      font-size: 0.95rem;
      transition: border-color 0.2s;
      font-family: inherit;
    }

    .robbai-input-area input:focus {
      outline: none;
      border-color: #0284c7;
    }

    .robbai-input-area input:disabled {
      background: #f1f5f9;
      cursor: not-allowed;
      color: #94a3b8;
    }

    .robbai-input-area button {
      padding: 0.75rem 1.25rem;
      background: #0284c7;
      color: white;
      border: none;
      border-radius: 8px;
      font-size: 0.95rem;
      cursor: pointer;
      transition: background 0.2s;
      white-space: nowrap;
      font-family: inherit;
    }

    .robbai-input-area button:hover {
      background: #0369a1;
    }

    .robbai-input-area button:disabled {
      background: #94a3b8;
      cursor: not-allowed;
    }

    @media (max-width: 768px) {
      .robbai-container {
        bottom: 80px;
        right: 10px;
        left: 10px;
        width: auto;
        height: 500px;
      }
    }
  `;

  // Inject styles into page
  const styleEl = document.createElement('style');
  styleEl.textContent = styles;
  document.head.appendChild(styleEl);

  // Create widget HTML
  const widgetHTML = `
    <div class="robbai-widget">
      <button class="robbai-button" id="robbai-toggle">💬</button>
      <div class="robbai-container" id="robbai-container">
        <div class="robbai-header">
          <div>
            <h3>${config.name}</h3>
            <p>Ask me about Rob's experience</p>
          </div>
          <button class="robbai-close" id="robbai-close">×</button>
        </div>
        <div class="robbai-messages" id="robbai-messages"></div>
        <div class="robbai-input-area">
          <input 
            type="text" 
            id="robbai-input" 
            placeholder="Initializing..." 
            disabled
          />
          <button id="robbai-send" disabled>Send</button>
        </div>
      </div>
    </div>
  `;

  // Inject widget into page
  document.body.insertAdjacentHTML('beforeend', widgetHTML);

  // Get references to elements
  const toggleBtn = document.getElementById('robbai-toggle');
  const closeBtn = document.getElementById('robbai-close');
  const container = document.getElementById('robbai-container');
  const messagesEl = document.getElementById('robbai-messages');
  const inputEl = document.getElementById('robbai-input');
  const sendBtn = document.getElementById('robbai-send');

  // Toggle widget
  function toggleChat() {
    if (container.classList.contains('open')) {
      container.classList.remove('open');
      toggleBtn.classList.remove('hidden');
    } else {
      container.classList.add('open');
      toggleBtn.classList.add('hidden');
      inputEl.focus();
    }
  }

  toggleBtn.addEventListener('click', toggleChat);
  closeBtn.addEventListener('click', toggleChat);

  // Add message to chat
  function addMessage(content, role) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `robbai-message ${role}`;

    if (role === 'assistant') {
      messageDiv.innerHTML = `<div class="name">${config.name}</div>${content}`;
    } else {
      messageDiv.textContent = content;
    }

    messagesEl.appendChild(messageDiv);
    messagesEl.scrollTop = messagesEl.scrollHeight;

    return messageDiv;
  }

  // Stream greeting
  async function streamGreeting() {
    const greeting = `Hi! I'm ${config.name}, pronounced ${config.pronunciation}, Rob's AI assistant. Ask me about his experience, skills, or projects!`;
    
    const messageDiv = document.createElement('div');
    messageDiv.className = 'robbai-message assistant';
    messageDiv.innerHTML = `<div class="name">${config.name}</div>`;
    
    const contentSpan = document.createElement('span');
    messageDiv.appendChild(contentSpan);
    messagesEl.appendChild(messageDiv);

    for (let i = 0; i < greeting.length; i++) {
      contentSpan.textContent += greeting[i];
      messagesEl.scrollTop = messagesEl.scrollHeight;
      await new Promise(resolve => setTimeout(resolve, 30));
    }

    inputEl.disabled = false;
    sendBtn.disabled = false;
    inputEl.placeholder = 'Ask a question...';
  }

  // Send message
  async function sendMessage() {
    const message = inputEl.value.trim();
    if (!message) return;

    inputEl.disabled = true;
    sendBtn.disabled = true;

    addMessage(message, 'user');
    inputEl.value = '';

    const loadingDiv = addMessage('Thinking...', 'assistant loading');

    try {
      const response = await fetch(`${API_BASE}/ai/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message }),
      });

      if (!response.ok) throw new Error('Failed to get response');

      const data = await response.json();
      loadingDiv.remove();
      addMessage(data.response, 'assistant');
    } catch (error) {
      loadingDiv.remove();
      addMessage('Sorry, I encountered an error. Please try again.', 'assistant');
      console.error('Chat error:', error);
    }

    inputEl.disabled = false;
    sendBtn.disabled = false;
    inputEl.focus();
  }

  // Handle Enter key
  inputEl.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
  });

  sendBtn.addEventListener('click', sendMessage);

  // Pre-warm Lambda
  fetch(`${API_BASE}/health`).catch(() => {});

  // Periodic health checks (only when page is visible)
  setInterval(() => {
    if (document.visibilityState === 'visible') {
      fetch(`${API_BASE}/health`).catch(() => {});
    }
  }, 180000);

  // Start greeting
  streamGreeting();

})();
