import { getCurrentUser, isAdmin } from './api.js';
import { initNav } from './nav.js';

async function initHome() {
  await initNav();
  const user = await getCurrentUser();
  const guestView = document.getElementById('guest-view');
  const authView = document.getElementById('auth-view');

  if (user) {
    guestView.hidden = true;
    authView.hidden = false;
    const adminCard = document.getElementById('admin-card');
    if (adminCard) {
      adminCard.hidden = !isAdmin(user);
    }
  } else {
    guestView.hidden = false;
    authView.hidden = true;
  }
}

initHome();
