import { initNav } from './nav.js';

const MESSAGES = {
  default: 'You have been logged out successfully.',
  password: 'Your password was updated. Please sign in again.',
  deactivated: 'Your account has been deactivated and you have been logged out.',
  deleted: 'Your account has been permanently deleted.',
};

async function initLogout() {
  await initNav();
  const params = new URLSearchParams(window.location.search);
  const reason = params.get('reason') || 'default';
  const messageEl = document.getElementById('logout-message');
  messageEl.textContent = MESSAGES[reason] || MESSAGES.default;
}

initLogout();
