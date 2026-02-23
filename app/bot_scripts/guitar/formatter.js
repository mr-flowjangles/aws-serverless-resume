/**
 * Guitar Bot Formatter
 * 
 * Detects tab diagrams and renders them with proper monospace formatting.
 * Also handles triad position tables with structured display.
 */

function guitarFormatMessage(text, container) {
  // Check if this contains tab diagrams
  if (text.includes('===') && (text.includes('DGB') || text.includes('GBE'))) {
    container.innerHTML = formatTriadPosition(text);
    return;
  }
  
  // Check for simple tab notation (e|-- B|-- G|-- etc.)
  if (text.match(/[eBGDAE]\|--\d+--\|/)) {
    container.innerHTML = formatTabSection(text);
    return;
  }
  
  // Default: plain text with line breaks
  container.innerHTML = text.replace(/\n/g, '<br>');
}

function formatTriadPosition(text) {
  const lines = text.split('\n');
  let html = '';
  let inTabSection = false;
  let tabLines = [];
  
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    
    // Section headers
    if (line.includes('=== DGB') || line.includes('=== GBE')) {
      // Flush any pending tab lines
      if (tabLines.length > 0) {
        html += renderTabTable(tabLines);
        tabLines = [];
      }
      
      const stringSet = line.includes('DGB') ? 'DGB' : 'GBE';
      html += `<div class="tab-section-header">${stringSet} String Set</div>`;
      inTabSection = true;
      continue;
    }
    
    // Tab header row (chord names)
    if (inTabSection && line.match(/\([a-z0-9]+\)/i) && !line.includes('|')) {
      if (tabLines.length > 0) {
        html += renderTabTable(tabLines);
        tabLines = [];
      }
      tabLines.push({ type: 'header', content: line });
      continue;
    }
    
    // Tab fret row
    if (inTabSection && line.match(/[eBGD]\|--/)) {
      tabLines.push({ type: 'frets', content: line });
      continue;
    }
    
    // End of tab section
    if (inTabSection && line.trim() === '') {
      if (tabLines.length > 0) {
        html += renderTabTable(tabLines);
        tabLines = [];
      }
      inTabSection = false;
      continue;
    }
    
    // Regular text
    if (line.startsWith('Key of')) {
      html += `<div class="position-title">${line}</div>`;
    } else if (line.startsWith('Anchor:')) {
      html += `<div class="position-anchor">${line}</div>`;
    } else if (line.startsWith('Target range:')) {
      html += `<div class="position-range">${line}</div>`;
    } else if (line.startsWith('You can choose')) {
      html += `<div class="position-note">${line}</div>`;
    } else if (line.trim()) {
      html += `<div>${line}</div>`;
    }
  }
  
  // Flush remaining tab lines
  if (tabLines.length > 0) {
    html += renderTabTable(tabLines);
  }
  
  return `<div class="triad-position">${html}</div>`;
}

function renderTabTable(tabLines) {
  if (tabLines.length === 0) return '';
  
  // Parse header to get chord names
  const headerLine = tabLines.find(l => l.type === 'header');
  const fretLines = tabLines.filter(l => l.type === 'frets');
  
  if (!headerLine || fretLines.length === 0) {
    // Fallback to preformatted
    return `<pre class="tab-pre">${tabLines.map(l => l.content).join('\n')}</pre>`;
  }
  
  // Parse chord names from header
  // Format: "G (1st)     Am (root)   Bm (1st)..."
  const chordMatches = headerLine.content.match(/(\w+#?\s*\([^)]+\))/g) || [];
  const chords = chordMatches.map(c => {
    const match = c.match(/(\w+#?)\s*\(([^)]+)\)/);
    return match ? { name: match[1], inversion: match[2] } : { name: c, inversion: '' };
  });
  
  // Build HTML table
  let html = '<table class="tab-table"><thead><tr>';
  
  // Header row with chord names
  for (const chord of chords) {
    html += `<th><span class="chord-name">${chord.name}</span><span class="chord-inv">(${chord.inversion})</span></th>`;
  }
  html += '</tr></thead><tbody>';
  
  // Fret rows
  for (const fretLine of fretLines) {
    html += '<tr>';
    
    // Parse fret values: "B|--8--|     B|--5--|..."
    const fretMatches = fretLine.content.match(/([eBGDA])\|--?(\d+)--\|/g) || [];
    
    for (const fretMatch of fretMatches) {
      const match = fretMatch.match(/([eBGDA])\|--?(\d+)--\|/);
      if (match) {
        const stringName = match[1];
        const fretNum = match[2];
        html += `<td><span class="string-name">${stringName}</span><span class="fret-num">${fretNum}</span></td>`;
      }
    }
    html += '</tr>';
  }
  
  html += '</tbody></table>';
  return html;
}

function formatTabSection(text) {
  // Wrap any tab notation in preformatted block
  return `<pre class="tab-pre">${text}</pre>`;
}

// Register the formatter
window.BOT_CONFIG = window.BOT_CONFIG || {};
window.BOT_CONFIG.formatMessage = guitarFormatMessage;
