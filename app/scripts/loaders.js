/**
 * Data Loading Functions
 * Functions to fetch and display resume data from the API
 */

import { API_BASE } from '/scripts/api.js';

async function loadProfile(container) {
  const response = await fetch(`${API_BASE}/resume/profile`);
  const data = await response.json();

  container.innerHTML = `
    <div class="experience-item">
      <h3>${data.name}</h3>
      <p class="company">${data.title}</p>
      <p class="description">${data.summary}</p>
      <p><strong>Location:</strong> ${data.location}</p>
      ${data.email ? `<p><strong>Email:</strong> ${data.email}</p>` : ''}
    </div>
    ${
      data.professional_summary
        ? `
      <div class="experience-item" style="margin-top: 1.5rem;">
        <h3>Professional Summary</h3>
        <p class="description">${data.professional_summary}</p>
      </div>
    `
        : ""
    }
  `;
}

async function loadExperience(container) {
  const response = await fetch(`${API_BASE}/resume/work-experience`);
  const data = await response.json();

  // Separate main experience from additional experience
  const mainExperience = data.items.filter(exp => !exp.is_additional);
  const additionalExperience = data.items.filter(exp => exp.is_additional);

  let html = "";
  
  // Render main experience as cards
  mainExperience.forEach((exp) => {
    const endDate = exp.is_current ? "present" : exp.end_date;
    html += `
      <div class="experience-item">
        <div class="experience-header">
          <div>
            <h3>${exp.job_title}</h3>
            <p class="company">${exp.company_name}</p>
          </div>
          <span class="date">${exp.start_date} – ${endDate}</span>
        </div>
        <p class="description">${exp.description}</p>
        <ul class="highlights">
          ${exp.accomplishments.map((h) => `<li>${h}</li>`).join("")}
        </ul>
      </div>
    `;
  });

  // Render additional experience as bulleted list
  if (additionalExperience.length > 0) {
    html += `
      <div class="additional-experience">
        <h3>Additional Experience</h3>
        <ul>
          ${additionalExperience.map(exp => {
            const startYear = exp.start_date ? exp.start_date.substring(0, 4) : '';
            const endYear = exp.end_date ? exp.end_date.substring(0, 4) : (exp.is_current ? 'Present' : '');
            const yearRange = startYear && endYear ? `(${startYear} – ${endYear})` : '';
            return `<li>${exp.job_title}, ${exp.company_name} ${yearRange}</li>`;
          }).join('')}
        </ul>
      </div>
    `;
  }

  container.innerHTML = html;
}

async function loadSkills(container) {
  const response = await fetch(`${API_BASE}/resume/skills`);
  const data = await response.json();

  let html = '<div class="skills-grid">';
  data.items.forEach((skillItem) => {
    html += `
      <div class="skill-category">
        <h3>${skillItem.category}</h3>
        <div class="skill-tags">
          ${skillItem.skills.map((s) => `<span class="skill-tag">${s}</span>`).join("")}
        </div>
      </div>
    `;
  });
  html += "</div>";

  container.innerHTML = html;
}

async function loadEducation(container) {
  const response = await fetch(`${API_BASE}/resume/education`);
  const data = await response.json();

  let html = "";
  data.items.forEach((edu) => {
    // Format date range with defensive checks
    let dateRange = '';
    const hasStartDate = edu.start_date && edu.start_date !== 'nan';
    const hasEndDate = edu.end_date && edu.end_date !== 'nan';

    if (hasStartDate && hasEndDate) {
      dateRange = `${edu.start_date} – ${edu.end_date}`;
    } else if (hasStartDate) {
      dateRange = edu.start_date;
    } else if (hasEndDate) {
      dateRange = edu.end_date;
    }

    html += `
      <div class="experience-item">
        <div class="experience-header">
          <div>
            <h3>${edu.degree}</h3>
            <p class="company">${edu.institution}</p>
          </div>
          ${dateRange ? `<span class="date">${dateRange}</span>` : ''}
        </div>
        ${edu.description ? `<p class="description">${edu.description}</p>` : ""}
      </div>
    `;
  });

  container.innerHTML = html;
}

async function loadProjects(container) {
  const response = await fetch(`${API_BASE}/resume/projects`);
  const data = await response.json();

  let html = "";
  data.items.forEach((proj) => {
    html += `
      <div class="project-item">
        <h3>${proj.name}</h3>
        <p class="description">${proj.description}</p>
        <div class="skill-tags">
          ${proj.tech.map((t) => `<span class="skill-tag">${t}</span>`).join("")}
        </div>
        <p style="margin-top: 1rem;">
          ${proj.github ? `<a href="${proj.github}" target="_blank">GitHub</a>` : ""}
          ${proj.liveUrl ? `<a href="${proj.liveUrl}" target="_blank">Live Demo</a>` : ""}
        </p>
      </div>
    `;
  });

  container.innerHTML = html;
}

async function loadHeaderData() {
  try {
    const response = await fetch(`${API_BASE}/resume/profile`);
    const data = await response.json();

    // Update page title
    document.title = `${data.name} - ${data.title}`;

    // Update header with profile data
    document.getElementById("header-name").textContent = data.name;
    document.getElementById("header-title").textContent = data.title;

    // Update photo
    document.getElementById("header-photo").src = data.photo;

    // Update links
    document.getElementById("pdf-link").href = data.resume_pdf;
    document.getElementById("linkedin-link").href = data.linkedin;
    document.getElementById("github-link").href = data.github;
  } catch (error) {
    console.error("Error loading header:", error);
  }
}

export {
  loadProfile,
  loadExperience,
  loadSkills,
  loadEducation,
  loadProjects,
  loadHeaderData
};
