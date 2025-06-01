/**
 * Configuration utilities for the application
 * Gets API base URL from environment variables with fallback
 */

// Declare the global ENV variable that will be set in the HTML
declare global {
  interface Window {
    ENV?: {
      API_BASE_URL?: string;
    };
  }
}

/**
 * Gets the API base URL from the environment variable or uses default
 * @returns {string} The API base URL
 */
export function getApiBaseUrl(): string {
  console.log('getApiBaseUrl called', window.ENV?.API_BASE_URL);
  if (window.ENV?.API_BASE_URL) {
    return window.ENV.API_BASE_URL;
  }

  // Default fallback
  return 'http://localhost:8000';
}

/**
 * Builds a complete API URL from a path
 * @param {string} path - The API endpoint path
 * @returns {string} The complete API URL
 */
export function buildApiUrl(path: string): string {
  const baseUrl = getApiBaseUrl();
  // Ensure path starts with a slash
  const normalizedPath = path.startsWith('/') ? path : `/${path}`;
  return `${baseUrl}${normalizedPath}`;
}
