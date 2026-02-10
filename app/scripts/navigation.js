/**
 * Navigation and Initialization
 * Handles section switching, mobile behavior, and page initialization
 */

import {
  loadProfile,
  loadExperience,
  loadSkills,
  loadEducation,
  loadHeaderData,
} from "/scripts/loaders.js";
import { loadArchitecture } from "/scripts/architecture.js";

// Navigation elements
const navLinks = document.querySelectorAll(".nav-link");
const sections = document.querySelectorAll(".content-section");

/**
 * Show a specific section (desktop) or scroll to it (mobile)
 */
function showSection(sectionId) {
  const isMobile = window.innerWidth <= 768;

  if (!isMobile) {
    // Desktop: hide all, show selected
    sections.forEach((s) => s.classList.remove("active"));
    navLinks.forEach((l) => l.classList.remove("active"));

    const section = document.getElementById(sectionId);
    const link = document.querySelector(`[data-section="${sectionId}"]`);

    if (section) section.classList.add("active");
    if (link) link.classList.add("active");
  }

  // Load data if not already loaded
  loadSectionData(sectionId);
}

/**
 * Load data for a specific section
 */
async function loadSectionData(section) {
  const container = document.getElementById(section);

  try {
    const h2 = container.querySelector("h2");
    const h2Text = h2 ? h2.textContent : "";

    switch (section) {
      case "about":
        await loadProfile(container);
        break;
      case "experience":
        await loadExperience(container);
        break;
      case "skills":
        await loadSkills(container);
        break;
      case "education":
        await loadEducation(container);
        break;
      case "architecture":
        await loadArchitecture();
        break;
    }

    // Re-add h2 if it existed and was removed
    if (h2Text && !container.querySelector("h2")) {
      const newH2 = document.createElement("h2");
      newH2.textContent = h2Text;
      container.insertBefore(newH2, container.firstChild);
    }
  } catch (error) {
    container.innerHTML = `<div class="error">Error loading data: ${error.message}</div>`;
  }
}

/**
 * Initialize navigation event listeners
 */
function initNavigation() {
  navLinks.forEach((link) => {
    link.addEventListener("click", (e) => {
      e.preventDefault();
      const section = link.dataset.section;
      showSection(section);
    });
  });
}

/**
 * Initialize page on load
 */
function initPage() {
  const isMobile = window.innerWidth <= 768;

  if (isMobile) {
    // Load all sections for mobile vertical scroll
    loadSectionData("about");
    loadSectionData("experience");
    loadSectionData("skills");
    loadSectionData("education");
    loadSectionData("architecture");

    // Collapse all sections except About Me after loading
    setTimeout(() => {
      document.querySelectorAll(".content-section").forEach((section) => {
        if (section.id !== "about") {
          section.classList.add("collapsed");
        }
      });
    }, 500);

    // Setup collapsible sections on mobile (click h2 to toggle)
    document.addEventListener("click", function (e) {
      if (e.target.tagName === "H2" && e.target.closest(".content-section")) {
        e.target.parentElement.classList.toggle("collapsed");
      }
    });
  } else {
    // Desktop - load only about section
    loadSectionData("about");
  }

  // Load header data
  loadHeaderData();
}

// Initialize everything when DOM is ready
initNavigation();
initPage();

export { showSection, loadSectionData };
