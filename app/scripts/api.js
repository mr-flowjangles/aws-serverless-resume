/**
 * API Configuration
 */

// Determine API base URL based on environment
const API_BASE =
  window.location.hostname === "localhost" ||
  window.location.hostname === "127.0.0.1"
    ? "/api"  // Local Docker environment
    : "https://qehzqmqmwg.execute-api.us-east-1.amazonaws.com/prod/api";  // Production

export { API_BASE };
