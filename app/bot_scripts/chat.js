/**
 * Bot Factory — Chat Module
 * 
 * Handles chat messaging, typing indicators, and suggestion chips.
 * Configurable via BOT_CONFIG object set in the HTML page.
 * 
 * Required: Set window.BOT_CONFIG before loading this script.
 *   window.BOT_CONFIG = {
 *     apiUrl: '/api/guitar',
 *     botName: 'GuitarBot',
 *     placeholder: 'Ask about guitar...'
 *   };
 * 
 * Optional: Set window.BOT_CONFIG.formatMessage to a function that
 * takes (text, containerDiv) and handles custom rendering.
 * If not set, messages render as plain text.
 */

const chatMessages = document.getElementById('chatMessages');
const chatInput = document.getElementById('chatInput');
const chatSuggestions = document.getElementById('chatSuggestions');

const config = window.BOT_CONFIG || {
    apiUrl: '/api/bot',
    botName: 'Bot',
    placeholder: 'Type a message...'
};


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
async function sendMessage() {
    const message = chatInput.value.trim();
    if (!message) return;

    addMessage(message, 'user');
    chatInput.value = '';

    // Hide suggestions after first message
    if (chatSuggestions) {
        chatSuggestions.style.display = 'none';
    }

    const typing = showTyping();

    try {
        const response = await fetch(`${config.apiUrl}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message })
        });

        const data = await response.json();
        typing.remove();
        addMessage(data.response, 'bot');
    } catch (error) {
        typing.remove();
        addMessage("Sorry, I couldn't connect. Try again in a moment.", 'bot');
    }
}


/**
 * Default message formatter — plain text with line breaks
 */
function defaultFormatMessage(text, container) {
    const lines = text.split('\n');
    for (const line of lines) {
        container.appendChild(document.createTextNode(line + '\n'));
    }
}


/**
 * Add a message bubble to the chat
 */
function addMessage(text, type) {
    const div = document.createElement('div');
    div.className = `chat-message ${type}`;

    if (type === 'bot') {
        const label = document.createElement('div');
        label.className = 'bot-label';
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
    const div = document.createElement('div');
    div.className = 'typing-indicator';
    div.innerHTML = '<span></span><span></span><span></span>';
    chatMessages.appendChild(div);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    return div;
}


// Enter key sends message
chatInput.addEventListener('keydown', function(e) {
    if (e.key === 'Enter') sendMessage();
});

// Warm up embedding cache on page load
fetch(`${config.apiUrl}/warmup`).catch(() => {});
