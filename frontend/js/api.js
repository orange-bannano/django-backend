import { generateIdempotencyKey } from './idempotency.js';

const config = window.APP_CONFIG || { apiBase: '' };

function apiUrl(path) {
  const base = (config.apiBase || '').replace(/\/$/, '');
  return `${base}${path}`;
}

async function parseResponse(response) {
  const contentType = response.headers.get('content-type') || '';
  if (contentType.includes('application/json')) {
    const data = await response.json();
    return { ok: response.ok, status: response.status, data };
  }
  const text = await response.text();
  return { ok: response.ok, status: response.status, data: { error: text || response.statusText } };
}

export async function apiRequest(path, options = {}) {
  const { idempotent = false, ...fetchOptions } = options;
  const headers = new Headers(fetchOptions.headers || {});

  if (fetchOptions.body && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json');
  }

  if (idempotent) {
    headers.set('Idempotency-Key', generateIdempotencyKey());
  }

  const response = await fetch(apiUrl(path), {
    ...fetchOptions,
    headers,
    credentials: 'include',
  });

  return parseResponse(response);
}

export async function getCurrentUser() {
  const result = await apiRequest('/api/me/');
  if (!result.ok) {
    return null;
  }
  return result.data.user;
}

export function isAdmin(user) {
  if (!user) return false;
  if (user.is_staff) return true;
  return (user.groups || []).some((group) => group.name === 'Admin');
}

export async function login(email, password) {
  return apiRequest('/api/login/', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  });
}

export async function logout() {
  return apiRequest('/api/logout/', { method: 'POST' });
}

export async function listNotes(params = {}) {
  const search = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value === undefined || value === null || value === '') return;
    if (key === 'title' && Array.isArray(value)) {
      value.forEach((t) => search.append('title', t));
    } else {
      search.set(key, String(value));
    }
  });
  const query = search.toString();
  return apiRequest(`/api/notes/${query ? `?${query}` : ''}`);
}

export async function createNote(title, body) {
  return apiRequest('/api/notes/', {
    method: 'POST',
    idempotent: true,
    body: JSON.stringify({ title, body }),
  });
}

export async function updateNote(noteId, title, body) {
  return apiRequest('/api/notes/', {
    method: 'PUT',
    idempotent: true,
    body: JSON.stringify({ note_id: noteId, title, body }),
  });
}

export async function deleteNote(noteId) {
  return apiRequest('/api/notes/', {
    method: 'DELETE',
    idempotent: true,
    body: JSON.stringify({ note_id: noteId }),
  });
}

export async function archiveNote(noteId) {
  return apiRequest(`/api/notes/${noteId}/archive/`, {
    method: 'POST',
    idempotent: true,
  });
}

export async function getIdempotencyFlag() {
  return apiRequest('/api/idempotency/');
}

export async function setIdempotencyFlag(enabled) {
  const body = enabled === undefined ? '{}' : JSON.stringify({ enabled });
  return apiRequest('/api/idempotency/', {
    method: 'POST',
    body,
  });
}

export async function listUsers() {
  return apiRequest('/api/users/');
}

export async function listGroups() {
  return apiRequest('/api/groups/');
}

export async function registerUser(payload) {
  return apiRequest('/api/register/', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function createGroup(group, permission) {
  return apiRequest('/api/register-group/', {
    method: 'POST',
    body: JSON.stringify({ group, permission }),
  });
}

export async function deactivateAccount() {
  return apiRequest('/api/deactivate/', { method: 'POST' });
}

export async function deleteAccount() {
  return apiRequest('/api/delete/', { method: 'DELETE' });
}

export async function updatePassword(password) {
  return apiRequest('/api/reset/', {
    method: 'POST',
    body: JSON.stringify({ password }),
  });
}

export function formatError(result) {
  if (!result || !result.data) return 'Request failed.';
  if (result.data.error) return result.data.error;
  if (result.data.errors) {
    return Object.entries(result.data.errors)
      .map(([field, message]) => `${field}: ${message}`)
      .join('; ');
  }
  return `Request failed (${result.status}).`;
}
