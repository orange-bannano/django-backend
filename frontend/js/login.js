import { login, formatError, getCurrentUser } from './api.js';
import { initNav, showAlert, hideAlert } from './nav.js';

async function initLogin() {
  await initNav();
  const user = await getCurrentUser();
  if (user) {
    window.location.href = '/';
    return;
  }

  const form = document.getElementById('login-form');
  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    hideAlert('login-alert');
    const submitBtn = form.querySelector('button[type="submit"]');
    submitBtn.disabled = true;

    const email = form.email.value.trim();
    const password = form.password.value;

    const result = await login(email, password);
    if (result.ok) {
      window.location.href = '/';
      return;
    }

    showAlert('login-alert', formatError(result));
    submitBtn.disabled = false;
  });
}

initLogin();
