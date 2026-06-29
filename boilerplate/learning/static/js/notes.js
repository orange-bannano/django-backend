import {
  listNotes,
  createNote,
  updateNote,
  deleteNote,
  archiveNote,
  formatError,
  isAdmin,
} from './api.js';
import { initNav, showAlert, hideAlert } from './nav.js';

let currentUser = null;
let currentMeta = null;
let loadedNotes = [];

function noteCard(note) {
  const archived = note.is_archived ? ' <span class="badge badge-muted">Archived</span>' : '';
  return `
    <article class="note-card" data-id="${note.id}">
      <header class="note-card-header">
        <h3>#${note.id} ${escapeHtml(note.title)}${archived}</h3>
        <time>${formatDate(note.created_at)}</time>
      </header>
      <p class="note-body">${escapeHtml(note.body || '(empty)')}</p>
      <footer class="note-card-footer">
        <button type="button" class="btn btn-ghost btn-sm edit-note" data-id="${note.id}">Edit</button>
        <button type="button" class="btn btn-ghost btn-sm archive-note" data-id="${note.id}">Toggle archive</button>
        ${currentUser && isAdmin(currentUser) ? `<button type="button" class="btn btn-danger btn-sm delete-note" data-id="${note.id}">Delete</button>` : ''}
      </footer>
    </article>
  `;
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

function formatDate(iso) {
  if (!iso) return '';
  return new Date(iso).toLocaleString();
}

function getFilterParams() {
  const form = document.getElementById('filter-form');
  const limit = parseInt(form.limit.value, 10) || 3;
  const offset = parseInt(form.offset.value, 10) || 0;
  const sort = form.sort.value;
  const exactNoteId = form.exact_note_id.value.trim();
  const titleKeyword = form.title_keyword.value.trim();
  const includeArchived = form.include_archived.checked ? '1' : undefined;

  const params = { limit, offset, sort };
  if (exactNoteId) {
    params.exact_note_id = exactNoteId;
  } else if (titleKeyword) {
    params.title = [titleKeyword];
  }
  if (includeArchived) {
    params.include_archived = includeArchived;
  }
  return params;
}

function updatePagination(meta) {
  currentMeta = meta;
  const info = document.getElementById('pagination-info');
  const prevBtn = document.getElementById('prev-page');
  const nextBtn = document.getElementById('next-page');

  if (!meta) {
    info.textContent = '';
    prevBtn.disabled = true;
    nextBtn.disabled = true;
    return;
  }

  const start = meta.count === 0 ? 0 : meta.offset + 1;
  const end = Math.min(meta.offset + meta.limit, meta.count);
  info.textContent = `Showing ${start}–${end} of ${meta.count}`;

  prevBtn.disabled = meta.previous_offset === null || meta.previous_offset === undefined;
  nextBtn.disabled = meta.next_offset === null || meta.next_offset === undefined;
}

async function loadNotes() {
  hideAlert('notes-alert');
  const listEl = document.getElementById('notes-list');
  listEl.innerHTML = '<p class="muted">Loading notes…</p>';

  const params = getFilterParams();
  const result = await listNotes(params);

  if (!result.ok) {
    listEl.innerHTML = '';
    showAlert('notes-alert', formatError(result));
    updatePagination(null);
    return;
  }

  loadedNotes = result.data.notes || [];
  currentMeta = result.data.meta;

  if (loadedNotes.length === 0) {
    listEl.innerHTML = '<p class="muted">No notes match your filters.</p>';
  } else {
    listEl.innerHTML = loadedNotes.map(noteCard).join('');
    bindNoteActions();
  }

  updatePagination(currentMeta);
  document.getElementById('filter-form').offset.value = currentMeta?.offset ?? 0;
}

function bindNoteActions() {
  document.querySelectorAll('.edit-note').forEach((btn) => {
    btn.addEventListener('click', () => {
      const id = parseInt(btn.dataset.id, 10);
      const note = loadedNotes.find((n) => n.id === id);
      if (!note) return;
      document.getElementById('edit-note-id').value = id;
      document.getElementById('edit-title').value = note.title;
      document.getElementById('edit-body').value = note.body;
      document.getElementById('edit-panel').hidden = false;
      document.getElementById('edit-panel').scrollIntoView({ behavior: 'smooth' });
    });
  });

  document.querySelectorAll('.archive-note').forEach((btn) => {
    btn.addEventListener('click', async () => {
      hideAlert('notes-alert');
      btn.disabled = true;
      const result = await archiveNote(parseInt(btn.dataset.id, 10));
      if (!result.ok) {
        showAlert('notes-alert', formatError(result));
        btn.disabled = false;
        return;
      }
      await loadNotes();
    });
  });

  document.querySelectorAll('.delete-note').forEach((btn) => {
    btn.addEventListener('click', async () => {
      if (!confirm('Permanently delete this note?')) return;
      hideAlert('notes-alert');
      btn.disabled = true;
      const result = await deleteNote(parseInt(btn.dataset.id, 10));
      if (!result.ok) {
        showAlert('notes-alert', formatError(result));
        btn.disabled = false;
        return;
      }
      await loadNotes();
    });
  });
}

async function initNotes() {
  currentUser = await initNav({ requireAuth: true });
  if (!currentUser) return;

  document.getElementById('filter-form').addEventListener('submit', async (event) => {
    event.preventDefault();
    document.getElementById('filter-form').offset.value = 0;
    await loadNotes();
  });

  document.getElementById('reset-filters').addEventListener('click', () => {
    const form = document.getElementById('filter-form');
    form.limit.value = 3;
    form.offset.value = 0;
    form.sort.value = '-created_at';
    form.exact_note_id.value = '';
    form.title_keyword.value = '';
    form.include_archived.checked = false;
    loadNotes();
  });

  document.getElementById('prev-page').addEventListener('click', async () => {
    if (!currentMeta || currentMeta.previous_offset === null) return;
    document.getElementById('filter-form').offset.value = currentMeta.previous_offset;
    await loadNotes();
  });

  document.getElementById('next-page').addEventListener('click', async () => {
    if (!currentMeta || currentMeta.next_offset === null) return;
    document.getElementById('filter-form').offset.value = currentMeta.next_offset;
    await loadNotes();
  });

  document.getElementById('create-form').addEventListener('submit', async (event) => {
    event.preventDefault();
    hideAlert('notes-alert');
    const form = event.target;
    const submitBtn = form.querySelector('button[type="submit"]');
    submitBtn.disabled = true;

    const result = await createNote(form.title.value.trim(), form.body.value.trim());
    if (!result.ok) {
      showAlert('notes-alert', formatError(result));
      submitBtn.disabled = false;
      return;
    }

    form.reset();
    submitBtn.disabled = false;
    showAlert('notes-alert', 'Note created.', 'success');
    await loadNotes();
  });

  document.getElementById('edit-form').addEventListener('submit', async (event) => {
    event.preventDefault();
    hideAlert('notes-alert');
    const form = event.target;
    const submitBtn = form.querySelector('button[type="submit"]');
    submitBtn.disabled = true;

    const result = await updateNote(
      parseInt(form.note_id.value, 10),
      form.title.value.trim(),
      form.body.value.trim(),
    );
    if (!result.ok) {
      showAlert('notes-alert', formatError(result));
      submitBtn.disabled = false;
      return;
    }

    document.getElementById('edit-panel').hidden = true;
    submitBtn.disabled = false;
    showAlert('notes-alert', 'Note updated.', 'success');
    await loadNotes();
  });

  document.getElementById('cancel-edit').addEventListener('click', () => {
    document.getElementById('edit-panel').hidden = true;
  });

  await loadNotes();
}

initNotes();
