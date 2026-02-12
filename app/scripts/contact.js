/**
 * Contact Form Handling
 * Handles form submission with reCAPTCHA validation
 */
import { API_BASE } from "/scripts/api.js";

/**
 * Fix reCAPTCHA accessibility issues
 */
function fixRecaptchaAccessibility() {
  // Add aria-label to the hidden textarea
  const textarea = document.getElementById("g-recaptcha-response");
  if (textarea) {
    textarea.setAttribute("aria-label", "reCAPTCHA response");
    textarea.setAttribute("aria-hidden", "true");
  }

  // Add title to the reCAPTCHA iframe
  const iframe = document.querySelector("#contact-form iframe");
  if (iframe) {
    iframe.setAttribute("title", "reCAPTCHA verification");
  }
}

/**
 * Initialize contact form
 */
function initContactForm() {
  const form = document.getElementById("contact-form");
  if (!form) {
    console.warn("Contact form not found");
    return;
  }

  // Fix accessibility after a short delay to ensure reCAPTCHA is loaded
  setTimeout(fixRecaptchaAccessibility, 1000);

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    // Validate reCAPTCHA
    const recaptchaResponse = grecaptcha.getResponse();
    if (!recaptchaResponse) {
      alert("Please complete the reCAPTCHA");
      return;
    }

    // Collect form data
    const formData = {
      name: document.getElementById("name").value,
      email: document.getElementById("email").value,
      message: document.getElementById("message").value,
      recaptcha_token: recaptchaResponse,
    };

    try {
      // Submit to API
      const response = await fetch(`${API_BASE}/contact`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        alert("Message sent successfully!");
        e.target.reset();
        grecaptcha.reset(); // Reset reCAPTCHA
      } else {
        alert("Failed to send message. Please try again.");
      }
    } catch (error) {
      alert("Error sending message: " + error.message);
    }
  });
}

// Initialize when DOM is ready
initContactForm();

export { initContactForm };
