/**
 * RobbAI Architecture Display
 * Loads and displays the interactive architecture visualization
 */

async function loadArchitecture() {
  const container = document.getElementById('architecture-content');
  
  // Check if already loaded
  if (container.dataset.loaded === 'true') {
    return;
  }
  
  container.innerHTML = `
    <!-- SECTION 1: WEBSITE INFRASTRUCTURE -->
    <div style="background: linear-gradient(135deg, #f8fafc 0%, #e0f2fe 100%); padding: 2rem; border-radius: 12px; margin-bottom: 3rem; border-left: 6px solid #0284c7;">
      <h3 style="color: #0f172a; font-size: 1.75rem; margin-bottom: 1rem; display: flex; align-items: center; gap: 0.75rem;">
        <span style="font-size: 2rem;">🌐</span> Website Infrastructure
      </h3>
      <p style="color: #475569; margin-bottom: 2rem; line-height: 1.6;">
        Serverless AWS architecture powering the resume website with unified FastAPI codebase for local and production.
      </p>

      <!-- Site Components -->
      <h4 class="arch-section-title" style="font-size: 1.25rem;">Core Components</h4>
      <div class="arch-components">
        <div class="arch-column">
          <h4>Frontend Delivery</h4>
          <div class="arch-component">
            <div class="arch-component-name">CloudFront</div>
            <div class="arch-component-desc">Global CDN distribution</div>
          </div>
          <div class="arch-component">
            <div class="arch-component-name">S3</div>
            <div class="arch-component-desc">Static file hosting</div>
          </div>
        </div>

        <div class="arch-column">
          <h4>API Layer</h4>
          <div class="arch-component arch-aws">
            <div class="arch-component-name">API Gateway</div>
            <div class="arch-component-desc">REST endpoints</div>
          </div>
          <div class="arch-component arch-aws">
            <div class="arch-component-name">Lambda</div>
            <div class="arch-component-desc">FastAPI with Mangum</div>
          </div>
        </div>

        <div class="arch-column">
          <h4>Data Storage</h4>
          <div class="arch-component arch-aws">
            <div class="arch-component-name">DynamoDB</div>
            <div class="arch-component-desc">Resume content</div>
          </div>
        </div>
      </div>

      <!-- Local Development -->
      <h4 class="arch-section-title" style="font-size: 1.25rem;">Local Development</h4>
      <div class="arch-flow-steps">
        <div class="arch-step">
          <div class="arch-step-number">🐳</div>
          <h4>Docker Compose</h4>
          <p>Multi-container orchestration with Nginx reverse proxy</p>
        </div>
        <div class="arch-step">
          <div class="arch-step-number">⚡</div>
          <h4>LocalStack</h4>
          <p>AWS service simulation for DynamoDB</p>
        </div>
        <div class="arch-step">
          <div class="arch-step-number">🔄</div>
          <h4>Unified Code</h4>
          <p>Same FastAPI app runs in Docker and Lambda via Mangum adapter</p>
        </div>
      </div>
    </div>

    <!-- SECTION 2: ROBBAI CHATBOT -->
    <div style="background: linear-gradient(135deg, #fefce8 0%, #fef3c7 100%); padding: 2rem; border-radius: 12px; margin-bottom: 2rem; border-left: 6px solid #f59e0b;">
      <h3 style="color: #0f172a; font-size: 1.75rem; margin-bottom: 1rem; display: flex; align-items: center; gap: 0.75rem;">
        <span style="font-size: 2rem;">🤖</span> RobbAI Chatbot (RAG System)
      </h3>
      <p style="color: #475569; margin-bottom: 2rem; line-height: 1.6;">
        Production RAG implementation with semantic search, embeddings cache, and cold start optimization.
      </p>

      <!-- RobbAI Metrics -->
      <div class="arch-metrics">
        <div class="arch-metric">
          <div class="arch-metric-value">~6s</div>
          <div class="arch-metric-label">Response Time</div>
        </div>
        <div class="arch-metric">
          <div class="arch-metric-value">21</div>
          <div class="arch-metric-label">Cached Embeddings</div>
        </div>
        <div class="arch-metric">
          <div class="arch-metric-value">2</div>
          <div class="arch-metric-label">External APIs</div>
        </div>
        <div class="arch-metric">
          <div class="arch-metric-value">1.2s</div>
          <div class="arch-metric-label">Saved by Cache</div>
        </div>
      </div>

      <!-- Cold Start Optimization -->
      <div class="arch-optimization">
        <h3>🚀 Cold Start Optimization: "Sleight of Hand"</h3>
        <p>
          The frontend immediately pings the health endpoint on page load, warming the Lambda container and pre-loading 
          embeddings into memory while streaming a greeting message. By the time users submit their first question, 
          the system is warm and cached, reducing perceived response time from 9+ seconds to ~2 seconds.
        </p>
      </div>

      <!-- Chat Request Flow -->
      <h4 class="arch-section-title" style="font-size: 1.25rem;">Chat Request Flow</h4>
      <div class="arch-flow-steps">
      <div class="arch-step">
        <div class="arch-step-number">1</div>
        <h4>User Question</h4>
        <p>User submits question via chatbot widget</p>
        <div class="arch-timing">~0ms</div>
      </div>

      <div class="arch-step">
        <div class="arch-step-number">2</div>
        <h4>API Gateway</h4>
        <p>AWS routes request to Lambda</p>
        <div class="arch-timing">~50ms</div>
      </div>

      <div class="arch-step">
        <div class="arch-step-number">3</div>
        <h4>Query Embedding</h4>
        <p>OpenAI API converts question to vector</p>
        <div class="arch-timing">~3 seconds</div>
      </div>

      <div class="arch-step">
        <div class="arch-step-number">4</div>
        <h4>Semantic Search</h4>
        <p>Calculate similarity vs cached embeddings</p>
        <div class="arch-timing">~60ms</div>
      </div>

      <div class="arch-step">
        <div class="arch-step-number">5</div>
        <h4>Retrieve Matches</h4>
        <p>Return top 5 relevant resume chunks</p>
        <div class="arch-timing">~10ms</div>
      </div>

      <div class="arch-step">
        <div class="arch-step-number">6</div>
        <h4>Generate Response</h4>
        <p>Claude Sonnet 4 API creates answer</p>
        <div class="arch-timing">~2.6 seconds</div>
      </div>

      <div class="arch-step">
        <div class="arch-step-number">7</div>
        <h4>Log & Return</h4>
        <p>Save to DynamoDB, return to user</p>
        <div class="arch-timing">~100ms</div>
      </div>
    </div>

    <!-- RobbAI Components -->
    <h4 class="arch-section-title" style="font-size: 1.25rem;">RobbAI Components</h4>
    <div class="arch-components">
      <div class="arch-column">
        <h4>Frontend</h4>
        <div class="arch-component">
          <div class="arch-component-name">Chatbot Widget</div>
          <div class="arch-component-desc">JavaScript UI</div>
        </div>
        <div class="arch-component arch-cache">
          <div class="arch-component-name">Health Ping</div>
          <div class="arch-component-desc">Pre-warms Lambda</div>
        </div>
      </div>

      <div class="arch-column">
        <h4>Backend Processing</h4>
        <div class="arch-component arch-aws">
          <div class="arch-component-name">Lambda</div>
          <div class="arch-component-desc">FastAPI RAG engine</div>
        </div>
        <div class="arch-component arch-cache">
          <div class="arch-component-name">In-Memory Cache</div>
          <div class="arch-component-desc">21 embeddings</div>
        </div>
        <div class="arch-component arch-aws">
          <div class="arch-component-name">DynamoDB</div>
          <div class="arch-component-desc">ChatbotRAG + Logs</div>
        </div>
      </div>

      <div class="arch-column">
        <h4>External AI APIs</h4>
        <div class="arch-component arch-external">
          <div class="arch-component-name">OpenAI</div>
          <div class="arch-component-desc">text-embedding-3-small</div>
        </div>
        <div class="arch-component arch-external">
          <div class="arch-component-name">Anthropic Claude</div>
          <div class="arch-component-desc">Sonnet 4</div>
        </div>
      </div>
    </div>

    <!-- Chatbot Data Storage -->
    <h4 class="arch-section-title" style="font-size: 1.25rem;">Chatbot Data Storage</h4>
    <div class="arch-flow-steps">
      <div class="arch-step">
        <div class="arch-step-number">🧠</div>
        <h4>ChatbotRAG</h4>
        <p>21 pre-computed embeddings of resume chunks for semantic search</p>
      </div>

      <div class="arch-step">
        <div class="arch-step-number">📝</div>
        <h4>ChatbotLogs</h4>
        <p>Q&A history with sources and similarity scores for analysis</p>
      </div>
    </div>
  </div>

  <!-- Legend -->
    <div class="arch-legend">
      <div class="arch-legend-item">
        <div class="arch-legend-color arch-aws"></div>
        <span>AWS Services</span>
      </div>
      <div class="arch-legend-item">
        <div class="arch-legend-color arch-external"></div>
        <span>External APIs</span>
      </div>
      <div class="arch-legend-item">
        <div class="arch-legend-color arch-cache"></div>
        <span>Optimization</span>
      </div>
    </div>
  `;
  
  container.dataset.loaded = 'true';
}

export { loadArchitecture };
