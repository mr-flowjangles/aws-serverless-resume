/**
 * Architecture Display
 * Loads and displays the interactive architecture visualization
 */

async function loadArchitecture() {
  const container = document.getElementById('architecture-content');
  
  // Check if already loaded
  if (container.dataset.loaded === 'true') {
    return;
  }
  
  container.innerHTML = `
    <!-- SECTION 1: RESUME SITE -->
    <div style="background: linear-gradient(135deg, #f8fafc 0%, #e0f2fe 100%); padding: 2rem; border-radius: 12px; margin-bottom: 3rem; border-left: 6px solid #0284c7;">
      <h3 style="color: #0f172a; font-size: 1.75rem; margin-bottom: 1rem; display: flex; align-items: center; gap: 0.75rem;">
        <span style="font-size: 2rem;">🌐</span> Resume Site
      </h3>
      <p style="color: #475569; margin-bottom: 2rem; line-height: 1.6;">
        This site doesn't need this much infrastructure — but it's a useful sandbox for learning serverless AWS patterns end to end. One FastAPI codebase runs locally via Docker and in production via Lambda, fully deployed with Terraform. Includes a floating RobbAI chat widget powered by Bot Factory.
      </p>

      <!-- Core Components -->
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
          <h4>Data &amp; Email</h4>
          <div class="arch-component arch-aws">
            <div class="arch-component-name">DynamoDB</div>
            <div class="arch-component-desc">Resume content</div>
          </div>
          <div class="arch-component arch-aws">
            <div class="arch-component-name">SES</div>
            <div class="arch-component-desc">Contact form delivery</div>
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

    <!-- SECTION 2: BOT FACTORY -->
    <div style="background: linear-gradient(135deg, #f8fafc 0%, #fce7f3 100%); padding: 2rem; border-radius: 12px; margin-bottom: 3rem; border-left: 6px solid #9333ea;">
      <h3 style="color: #0f172a; font-size: 1.75rem; margin-bottom: 1rem; display: flex; align-items: center; gap: 0.75rem;">
        <span style="font-size: 2rem;">🤖</span> Bot Factory
      </h3>
      <p style="color: #475569; margin-bottom: 2rem; line-height: 1.6;">
        A reusable RAG chatbot platform extracted from this project into its own repo. Define a bot with YAML config, a system prompt, and knowledge base files — Bot Factory handles embeddings, retrieval, and response generation.
      </p>

      <!-- Bot Factory Components -->
      <h4 class="arch-section-title" style="font-size: 1.25rem;">Core Components</h4>
      <div class="arch-components">
        <div class="arch-column">
          <h4>AI Services</h4>
          <div class="arch-component arch-external">
            <div class="arch-component-name">Claude</div>
            <div class="arch-component-desc">Response generation via Bedrock</div>
          </div>
          <div class="arch-component arch-external">
            <div class="arch-component-name">Embeddings</div>
            <div class="arch-component-desc">Semantic search vectors</div>
          </div>
        </div>

        <div class="arch-column">
          <h4>Infrastructure</h4>
          <div class="arch-component arch-aws">
            <div class="arch-component-name">Lambda</div>
            <div class="arch-component-desc">SSE streaming via Function URL</div>
          </div>
          <div class="arch-component arch-aws">
            <div class="arch-component-name">S3</div>
            <div class="arch-component-desc">Bot configs &amp; knowledge data</div>
          </div>
        </div>

        <div class="arch-column">
          <h4>Data Layer</h4>
          <div class="arch-component arch-aws">
            <div class="arch-component-name">DynamoDB</div>
            <div class="arch-component-desc">Embeddings, logs, chat history, API keys</div>
          </div>
        </div>
      </div>

      <!-- Bot Definition -->
      <h4 class="arch-section-title" style="font-size: 1.25rem;">Bot Definition</h4>
      <div class="arch-flow-steps">
        <div class="arch-step">
          <div class="arch-step-number">📋</div>
          <h4>config.yml</h4>
          <p>Bot identity, model settings, RAG tuning, frontend config</p>
        </div>
        <div class="arch-step">
          <div class="arch-step-number">💬</div>
          <h4>prompt.yml</h4>
          <p>System prompt defining personality, tone, and response rules</p>
        </div>
        <div class="arch-step">
          <div class="arch-step-number">📚</div>
          <h4>data/*.yml</h4>
          <p>Knowledge base files — text or structured entries with search terms</p>
        </div>
      </div>
    </div>

    <!-- SECTION 3: ROBBAI CHAT WIDGET -->
    <div style="background: linear-gradient(135deg, #f8fafc 0%, #dcfce7 100%); padding: 2rem; border-radius: 12px; margin-bottom: 3rem; border-left: 6px solid #16a34a;">
      <h3 style="color: #0f172a; font-size: 1.75rem; margin-bottom: 1rem; display: flex; align-items: center; gap: 0.75rem;">
        <span style="font-size: 2rem;">💬</span> RobbAI — Chat Widget
      </h3>
      <p style="color: #475569; margin-bottom: 2rem; line-height: 1.6;">
        The floating chat bubble on this site connects directly to Bot Factory's streaming Lambda. No proxy — the browser talks straight to the Function URL over SSE.
      </p>

      <h4 class="arch-section-title" style="font-size: 1.25rem;">How It Works</h4>
      <div class="arch-flow-steps">
        <div class="arch-step">
          <div class="arch-step-number">1</div>
          <h4>Chat Widget</h4>
          <p>Self-contained JS/CSS on this site. Sends messages with bot_id and API key to Bot Factory Lambda.</p>
        </div>
        <div class="arch-step">
          <div class="arch-step-number">2</div>
          <h4>RAG Retrieval</h4>
          <p>Bot Factory embeds the query, searches DynamoDB for relevant knowledge chunks via cosine similarity.</p>
        </div>
        <div class="arch-step">
          <div class="arch-step-number">3</div>
          <h4>Claude via Bedrock</h4>
          <p>Retrieved context + system prompt sent to Claude. Response streams back token-by-token over SSE.</p>
        </div>
      </div>
    </div>

    <!-- Development Process -->
    <div style="background: #f8fafc; padding: 1.5rem; border-radius: 8px; margin-bottom: 2rem; border-left: 4px solid #64748b;">
      <p style="color: #475569; margin: 0; line-height: 1.6;">
        Both projects are built with <strong style="color: #0f172a;">Claude</strong> as a development partner — architecture decisions, code reviews, debugging, and refactoring. Less "AI wrote my code" and more "I have a really good sounding board."
      </p>
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
