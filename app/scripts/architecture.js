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
