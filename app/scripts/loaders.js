/**
 * Data Loading Functions
 *
 * Fetches ALL resume data in a single API call on first load,
 * caches the Promise so concurrent callers share one fetch.
 *
 * One fetch. Zero repeat calls.
 */

import { API_BASE } from "/scripts/api.js";

// ---------------------------------------------------------------------------
// Module-level cache — stores the Promise, not the result
// ---------------------------------------------------------------------------
let _resumePromise = null;

/**
 * Fetch all resume data and cache it.
 * Safe to call multiple times — only fetches once.
 * Caches the Promise itself so concurrent callers share one request.
 */
async function fetchResumeData() {
  if (!_resumePromise) {
    _resumePromise = fetch(`${API_BASE}/resume`).then((response) => {
      if (!response.ok) throw new Error("Failed to load resume data");
      return response.json();
    });
  }
  return _resumePromise;
}

// ---------------------------------------------------------------------------
// Section loaders — all read from cache
// ---------------------------------------------------------------------------

async function loadProfile(container) {
  const data = await fetchResumeData();
  const profile = data.profile;

  container.innerHTML = `
    <div class="experience-item">
      <h3>${profile.name}</h3>
      <p class="company">${profile.title}</p>
      <p class="description">${profile.summary}</p>
      <p><strong>Location:</strong> ${profile.location}</p>
      ${profile.email ? `<p><strong>Email:</strong> ${profile.email}</p>` : ""}
    </div>
    ${
      profile.professional_summary
        ? `
      <div class="experience-item" style="margin-top: 1.5rem;">
        <h3>Professional Summary</h3>
        <p class="description">${profile.professional_summary}</p>
      </div>
    `
        : ""
    }
  `;
}

async function loadExperience(container) {
  const data = await fetchResumeData();
  const items = data.work_experience;

  // Separate main experience from additional experience
  const mainExperience = items.filter((exp) => !exp.is_additional);
  const additionalExperience = items.filter((exp) => exp.is_additional);

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
          <span class="date">${exp.start_date} — ${endDate}</span>
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
          ${additionalExperience
            .map((exp) => {
              const startYear = exp.start_date
                ? exp.start_date.substring(0, 4)
                : "";
              const endYear = exp.end_date
                ? exp.end_date.substring(0, 4)
                : exp.is_current
                  ? "Present"
                  : "";
              const yearRange =
                startYear && endYear ? `(${startYear} — ${endYear})` : "";
              return `<li>${exp.job_title}, ${exp.company_name} ${yearRange}</li>`;
            })
            .join("")}
        </ul>
      </div>
    `;
  }

  container.innerHTML = html;
}

async function loadSkills(container) {
  const data = await fetchResumeData();
  const items = data.skills;

  let html = '<div class="skills-grid">';
  items.forEach((skillItem) => {
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
  const data = await fetchResumeData();
  const items = data.education;

  let html = "";
  items.forEach((edu) => {
    // Format date range with defensive checks
    let dateRange = "";
    const hasStartDate = edu.start_date && edu.start_date !== "nan";
    const hasEndDate = edu.end_date && edu.end_date !== "nan";

    if (hasStartDate && hasEndDate) {
      dateRange = `${edu.start_date} — ${edu.end_date}`;
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
          ${dateRange ? `<span class="date">${dateRange}</span>` : ""}
        </div>
        ${edu.description ? `<p class="description">${edu.description}</p>` : ""}
      </div>
    `;
  });

  container.innerHTML = html;
}

async function loadHeaderData() {
  try {
    const data = await fetchResumeData();
    const profile = data.profile;

    // Update page title
    document.title = `${profile.name} - ${profile.title}`;

    // Update header with profile data
    document.getElementById("header-name").textContent = profile.name;
    document.getElementById("header-title").textContent = profile.title;

    // Update photo
    document.getElementById("header-photo").src = profile.photo;

    // Update links
    document.getElementById("pdf-link").href = profile.resume_pdf;
    document.getElementById("linkedin-link").href = profile.linkedin;
    document.getElementById("github-link").href = profile.github;
  } catch (error) {
    console.error("Error loading header:", error);
  }
}

export {
  loadProfile,
  loadExperience,
  loadSkills,
  loadEducation,
  loadHeaderData,
};
