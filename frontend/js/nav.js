import { getCurrentUser, isAdmin, logout } from './api.js';

const PAGE_LINKS = [
  { href: '/', label: 'Home', paths: ['/', '/index.html'] },
  { href: '/login/', label: 'Login', paths: ['/login/', '/login.html'], guestOnly: true },
  { href: '/notes/', label: 'Notes', paths: ['/notes/', '/notes.html'], auth: true },
  { href: '/panel/', label: 'Admin Panel', paths: ['/panel/', '/panel.html'], admin: true },
  { href: '/account/', label: 'Account', paths: ['/account/', '/account.html'], auth: true },
];

function currentPath() {
  const path = window.location.pathname.replace(/\/$/, '') || '/';
  return path;
}

export async function initNav(options = {}) {
  const navRoot = document.getElementById('site-nav');
  if (!navRoot) return null;

  const user = await getCurrentUser();
  const path = currentPath();

  const links = PAGE_LINKS.filter((link) => {
    if (link.guestOnly && user) return false;
    if (link.auth && !user) return false;
    if (link.admin && !isAdmin(user)) return false;
    return true;
  });

  const linkItems = links
    .map((link) => {
      const active = link.paths.some((p) => (p.replace(/\/$/, '') || '/') === path);
      return `<a href="${link.href}" class="nav-link${active ? ' active' : ''}">${link.label}</a>`;
    })
    .join('');

  const adminLink = `<a href="${window.APP_CONFIG?.adminUrl || '/admin/'}" class="nav-link nav-link-external" target="_blank" rel="noopener">Django Admin</a>`;

  const userBadge = user
    ? `<span class="nav-user">${user.email || user.username}</span>`
    : '';

  const logoutBtn = user
    ? `<button type="button" id="logout-btn" class="btn btn-ghost btn-sm">Log out</button>`
    : '';

  navRoot.innerHTML = `
    <div class="nav-inner">
      <a href="/" class="nav-brand">Memo Office</a>
      <div class="nav-links">${linkItems}${adminLink}</div>
      <div class="nav-actions">${userBadge}${logoutBtn}</div>
    </div>
  `;

  const logoutButton = document.getElementById('logout-btn');
  if (logoutButton) {
    logoutButton.addEventListener('click', async () => {
      logoutButton.disabled = true;
      await logout();
      window.location.href = '/logout/';
    });
  }

  if (options.requireAuth && !user) {
    window.location.href = '/login/';
    return null;
  }

  if (options.requireAdmin && !isAdmin(user)) {
    window.location.href = '/';
    return null;
  }

  return user;
}

export function showAlert(containerId, message, type = 'error') {
  const el = document.getElementById(containerId);
  if (!el) return;
  el.hidden = false;
  el.className = `alert alert-${type}`;
  el.textContent = message;
}

export function hideAlert(containerId) {
  const el = document.getElementById(containerId);
  if (el) el.hidden = true;
}
