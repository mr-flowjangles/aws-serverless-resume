/**
 * Guitar Bot — Tab Formatter
 *
 * Detects guitar tablature lines in bot responses and wraps them
 * in .tab-block spans for monospace rendering. Regular text stays
 * in the body font.
 *
 * Registers itself on window.BOT_CONFIG.formatMessage so the shared
 * chat.js picks it up automatically at render time.
 *
 * Load this AFTER BOT_CONFIG is defined and BEFORE or AFTER chat.js —
 * the hook is checked per-message, not at init.
 */

const TAB_LINE = /^[eEBbGgDdAa]\|/;

function guitarFormatMessage(text, container) {
  const lines = text.split("\n");
  let inTab = false;

  for (const line of lines) {
    if (TAB_LINE.test(line.trim())) {
      inTab = true;
      const span = document.createElement("span");
      span.className = "tab-block";
      span.textContent = line;
      container.appendChild(span);
    } else {
      if (inTab) {
        container.appendChild(document.createElement("br"));
        inTab = false;
      }
      container.appendChild(document.createTextNode(line + "\n"));
    }
  }
}

window.BOT_CONFIG = window.BOT_CONFIG || {};
window.BOT_CONFIG.formatMessage = guitarFormatMessage;
