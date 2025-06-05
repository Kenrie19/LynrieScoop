import { decodeJwtPayload } from './cookies.js';

function getCookie(name: string): string | null {
  const cookies = document.cookie.split('; ');
  const found = cookies.find((row) => row.startsWith(name + '='));
  return found ? decodeURIComponent(found.split('=')[1]) : null;
}

document.addEventListener('DOMContentLoaded', () => {
  const token = getCookie('token');
  const isLoggedIn = !!token;
  const user = token ? decodeJwtPayload(token) : null;

  const authLinks = document.querySelectorAll('.auth-only');
  const guestLinks = document.querySelectorAll('.guest-only');
  const adminLinks = document.querySelectorAll('.admin-only');
  const myMoviesLink = document.querySelector('a[href="/views/my_movies"]')
    ?.parentElement as HTMLElement;
  const logoutLink = document.querySelector('.logout-link') as HTMLElement;

  // Toon of verberg auth- en guest-links
  authLinks.forEach((link) => {
    (link as HTMLElement).style.display = isLoggedIn ? 'inline' : 'none';
  });

  guestLinks.forEach((link) => {
    (link as HTMLElement).style.display = isLoggedIn ? 'none' : 'inline';
  });

  // Admin of gewone user?
  if (user && user.role === 'manager') {
    adminLinks.forEach((link) => {
      (link as HTMLElement).style.display = 'inline';
    });

    // Verberg "My Movies" voor admins
    if (myMoviesLink) {
      myMoviesLink.style.display = 'none';
    }
  } else {
    adminLinks.forEach((link) => {
      (link as HTMLElement).style.display = 'none';
    });
  }

  // Logout knop
  if (isLoggedIn && logoutLink) {
    logoutLink.style.display = 'inline';
  } else if (logoutLink) {
    logoutLink.style.display = 'none';
  }

  const logoutBtn = document.getElementById('logoutBtn');
  if (logoutBtn) {
    logoutBtn.addEventListener('click', (e) => {
      e.preventDefault();
      document.cookie = 'token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 UTC;';
      window.location.href = '/views/login';
    });
  }
});
