/*
  Frontend helper for the Learning API developer UI.

  - Reads CSRF token from cookie and attaches it to unsafe requests.
  - Provides helper functions for register/login/logout, listing/creating notes,
    archive action, and cursor-based pagination.
  - Keeps UI code deliberately simple and well-commented for beginners.

  Note: This file is for local development and learning only.
*/

// Utility: read a cookie value (used for csrftoken)
function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
  return null;
}

// Small logger to show responses in the UI
function log(msg) {
  const el = document.getElementById('log');
  el.textContent = `${new Date().toISOString()} - ${msg}\n` + el.textContent;
}

// Generic fetch wrapper that adds JSON headers, CSRF, and includes credentials
async function apiFetch(path, { method = 'GET', body = null } = {}) {
  const headers = { 'Accept': 'application/json' };
  let opts = { method, headers, credentials: 'same-origin' };

  if (body !== null) {
    headers['Content-Type'] = 'application/json';
    // Attach CSRF token for unsafe methods (POST/PUT/DELETE)
    const csrftoken = getCookie('csrftoken');
    if (csrftoken) headers['X-CSRFToken'] = csrftoken;
    opts.body = JSON.stringify(body);
  }

  const resp = await fetch(path, opts);
  let payload = null;
  try {
    payload = await resp.json();
  } catch (e) {
    payload = { error: 'Invalid JSON response' };
  }
  return { status: resp.status, payload };
}

// -------------------- API helpers --------------------

async function register() {
  const email = document.getElementById('reg-email').value;
  const password = document.getElementById('reg-password').value;
  const first = document.getElementById('reg-first').value;
  const { status, payload } = await apiFetch('/api/register/', { method: 'POST', body: { email, password, first_name: first } });
  log(`REGISTER ${status} ${JSON.stringify(payload)}`);
}

async function login() {
  const email = document.getElementById('login-email').value;
  const password = document.getElementById('login-password').value;
  const { status, payload } = await apiFetch('/api/login/', { method: 'POST', body: { email, password } });
  log(`LOGIN ${status} ${JSON.stringify(payload)}`);
}

async function logout() {
  const { status, payload } = await apiFetch('/api/logout/', { method: 'POST', body: {} });
  log(`LOGOUT ${status} ${JSON.stringify(payload)}`);
}

async function me() {
  const { status, payload } = await apiFetch('/api/me/');
  log(`ME ${status} ${JSON.stringify(payload)}`);
}

async function createNote() {
  const title = document.getElementById('note-title').value;
  const body = document.getElementById('note-body').value;
  const { status, payload } = await apiFetch('/api/notes/', { method: 'POST', body: { title, body } });
  log(`CREATE NOTE ${status} ${JSON.stringify(payload)}`);
}

async function listNotes() {
  const title = document.getElementById('filter-title').value;
  const includeArchived = document.getElementById('filter-archived').checked ? '1' : '0';
  const sort = document.getElementById('filter-sort').value;
  const limit = document.getElementById('filter-limit').value || '10';
  const offset = document.getElementById('filter-offset').value || '0';
  const params = new URLSearchParams();
  if (title) params.set('title', title);
  if (includeArchived === '1') params.set('include_archived', '1');
  if (sort) params.set('sort', sort);
  params.set('limit', limit);
  params.set('offset', offset);
  const { status, payload } = await apiFetch('/api/notes/?' + params.toString());
  log(`LIST NOTES ${status} ${JSON.stringify(payload)}`);
}

// Cursor pagination state (simple): store last cursor returned by server
let lastCursor = null;
async function listCursor() {
  const params = new URLSearchParams();
  if (lastCursor) params.set('cursor', lastCursor);
  const { status, payload } = await apiFetch('/api/notes-cursor/?' + params.toString());
  log(`CURSOR PAGE ${status} ${JSON.stringify(payload)}`);
  if (payload && payload.next_cursor) lastCursor = payload.next_cursor;
}

async function archiveNote() {
  const id = document.getElementById('archive-id').value;
  if (!id) { log('archive: missing id'); return; }
  const { status, payload } = await apiFetch(`/api/notes/${id}/archive/`, { method: 'POST', body: {} });
  log(`ARCHIVE ${status} ${JSON.stringify(payload)}`);
}

// -------------------- Event wiring --------------------
document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('btn-register').addEventListener('click', register);
  document.getElementById('btn-login').addEventListener('click', login);
  document.getElementById('btn-logout').addEventListener('click', logout);
  document.getElementById('btn-me').addEventListener('click', me);
  document.getElementById('btn-create-note').addEventListener('click', createNote);
  document.getElementById('btn-list-notes').addEventListener('click', listNotes);
  document.getElementById('btn-list-cursor').addEventListener('click', listCursor);
  document.getElementById('btn-archive').addEventListener('click', archiveNote);
});

