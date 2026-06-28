/**
 * Local fallback when /config.js is unavailable (e.g. static-only hosting).
 * In normal development, Django serves /config.js from .env via serve_frontend_config.
 */
window.APP_CONFIG = window.APP_CONFIG || {
  apiBase: '',
  adminUrl: '/admin/',
  siteBaseUrl: 'http://127.0.0.1:8000',
};
