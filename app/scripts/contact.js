/**
 * Contact Form Handling
 * Handles form submission with reCAPTCHA validation
 */

import { API_BASE } from '/scripts/api.js';

/**
 * Initialize contact form
 */
function initContactForm() {
  const form = document.getElementById("contact-form");
  
  if (!form) {
    console.warn("Contact form not found");
    return;
  }
  
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
