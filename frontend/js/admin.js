import {
  listUsers,
  listGroups,
  registerUser,
  createGroup,
  getIdempotencyFlag,
  setIdempotencyFlag,
  formatError,
} from './api.js';
import { initNav, showAlert, hideAlert } from './nav.js';

function renderUsers(users) {
  const tbody = document.querySelector('#users-table tbody');
  if (!users.length) {
    tbody.innerHTML = '<tr><td colspan="3" class="muted">No users found.</td></tr>';
    return;
  }
  tbody.innerHTML = users
    .map(
      (user) => `
    <tr>
      <td>${escapeHtml(user.username)}</td>
      <td>${user.is_active ? 'Yes' : 'No'}</td>
      <td>${user.is_logged_in ? 'Yes' : 'No'}</td>
    </tr>
  `,
    )
    .join('');
}

function renderGroups(groups) {
  const tbody = document.querySelector('#groups-table tbody');
  if (!groups.length) {
    tbody.innerHTML = '<tr><td colspan="3" class="muted">No groups found.</td></tr>';
    return;
  }
  tbody.innerHTML = groups
    .map(
      (group) => `
    <tr>
      <td>${group.id}</td>
      <td>${escapeHtml(group.name)}</td>
      <td><code>${(group.permissions || []).join(', ') || '—'}</code></td>
    </tr>
  `,
    )
    .join('');
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

async function refreshUsers() {
  const result = await listUsers();
  if (result.ok) {
    renderUsers(result.data.users || []);
  } else {
    showAlert('admin-alert', formatError(result));
  }
}

async function refreshGroups() {
  const result = await listGroups();
  if (result.ok) {
    renderGroups(result.data.groups || []);
  } else {
    showAlert('admin-alert', formatError(result));
  }
}

async function refreshIdempotency() {
  const result = await getIdempotencyFlag();
  const statusEl = document.getElementById('idempotency-status');
  if (result.ok) {
    const enabled = result.data.idempotency_enabled;
    statusEl.textContent = enabled ? 'Enabled' : 'Disabled';
    statusEl.className = `status-pill ${enabled ? 'status-on' : 'status-off'}`;
  } else {
    statusEl.textContent = 'Unknown';
    statusEl.className = 'status-pill';
  }
}

async function initAdmin() {
  await initNav({ requireAuth: true, requireAdmin: true });

  await Promise.all([refreshUsers(), refreshGroups(), refreshIdempotency()]);

  document.getElementById('refresh-users').addEventListener('click', refreshUsers);
  document.getElementById('refresh-groups').addEventListener('click', refreshGroups);

  document.getElementById('toggle-idempotency').addEventListener('click', async () => {
    hideAlert('admin-alert');
    const result = await setIdempotencyFlag(undefined);
    if (!result.ok) {
      showAlert('admin-alert', formatError(result));
      return;
    }
    await refreshIdempotency();
    showAlert('admin-alert', `Idempotency is now ${result.data.idempotency_enabled ? 'enabled' : 'disabled'}.`, 'success');
  });

  document.getElementById('set-idempotency-on').addEventListener('click', async () => {
    hideAlert('admin-alert');
    const result = await setIdempotencyFlag(true);
    if (!result.ok) {
      showAlert('admin-alert', formatError(result));
      return;
    }
    await refreshIdempotency();
    showAlert('admin-alert', 'Idempotency enabled.', 'success');
  });

  document.getElementById('set-idempotency-off').addEventListener('click', async () => {
    hideAlert('admin-alert');
    const result = await setIdempotencyFlag(false);
    if (!result.ok) {
      showAlert('admin-alert', formatError(result));
      return;
    }
    await refreshIdempotency();
    showAlert('admin-alert', 'Idempotency disabled.', 'success');
  });

  document.getElementById('create-user-form').addEventListener('submit', async (event) => {
    event.preventDefault();
    hideAlert('admin-alert');
    const form = event.target;
    const submitBtn = form.querySelector('button[type="submit"]');
    submitBtn.disabled = true;

    const groupsRaw = form.groups.value.trim();
    const payload = {
      email: form.email.value.trim(),
      password: form.password.value,
      user_name: form.user_name.value.trim() || undefined,
      first_name: form.first_name.value.trim() || undefined,
      last_name: form.last_name.value.trim() || undefined,
    };
    if (groupsRaw) {
      payload.groups = groupsRaw.split(',').map((g) => g.trim()).filter(Boolean);
    }

    const result = await registerUser(payload);
    if (!result.ok) {
      showAlert('admin-alert', formatError(result));
      submitBtn.disabled = false;
      return;
    }

    form.reset();
    submitBtn.disabled = false;
    showAlert('admin-alert', `User ${result.data.user.email} created.`, 'success');
    await refreshUsers();
  });

  document.getElementById('create-group-form').addEventListener('submit', async (event) => {
    event.preventDefault();
    hideAlert('admin-alert');
    const form = event.target;
    const submitBtn = form.querySelector('button[type="submit"]');
    submitBtn.disabled = true;

    const permissionsRaw = form.permission.value.trim();
    const permission = permissionsRaw
      ? permissionsRaw.split(',').map((p) => p.trim()).filter(Boolean)
      : ['view_note'];

    const result = await createGroup(form.group.value.trim(), permission);
    if (!result.ok) {
      showAlert('admin-alert', formatError(result));
      submitBtn.disabled = false;
      return;
    }

    form.reset();
    submitBtn.disabled = false;
    showAlert('admin-alert', `Group "${result.data.name}" created.`, 'success');
    await refreshGroups();
  });
}

initAdmin();
