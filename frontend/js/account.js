import { deactivateAccount, deleteAccount, updatePassword, formatError } from './api.js';
import { initNav, showAlert, hideAlert } from './nav.js';

async function initAccount() {
  await initNav({ requireAuth: true });

  document.getElementById('password-form').addEventListener('submit', async (event) => {
    event.preventDefault();
    hideAlert('account-alert');
    const form = event.target;
    const password = form.password.value;
    const confirm = form.password_confirm.value;

    if (password !== confirm) {
      showAlert('account-alert', 'Passwords do not match.');
      return;
    }

    const submitBtn = form.querySelector('button[type="submit"]');
    submitBtn.disabled = true;

    const result = await updatePassword(password);
    if (!result.ok) {
      showAlert('account-alert', formatError(result));
      submitBtn.disabled = false;
      return;
    }

    window.location.href = '/logout/?reason=password';
  });

  document.getElementById('deactivate-btn').addEventListener('click', async () => {
    if (!confirm('Deactivate your account? You will be logged out and cannot perform CRUD until reactivated by an admin.')) {
      return;
    }
    hideAlert('account-alert');
    const result = await deactivateAccount();
    if (!result.ok) {
      showAlert('account-alert', formatError(result));
      return;
    }
    window.location.href = '/logout/?reason=deactivated';
  });

  document.getElementById('delete-btn').addEventListener('click', async () => {
    if (!confirm('Permanently delete your account? This cannot be undone.')) {
      return;
    }
    hideAlert('account-alert');
    const result = await deleteAccount();
    if (!result.ok) {
      showAlert('account-alert', formatError(result));
      return;
    }
    window.location.href = '/logout/?reason=deleted';
  });
}

initAccount();
