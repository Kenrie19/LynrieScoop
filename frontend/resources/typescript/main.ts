import { decodeJwtPayload } from './cookies.js';

function getCookie(name: string): string | null {
  const cookies = document.cookie.split('; ');
  const found = cookies.find((row) => row.startsWith(name + '='));
  return found ? decodeURIComponent(found.split('=')[1]) : null;
}

document.addEventListener('DOMContentLoaded', () => {
  const token = getCookie('token');
  const authLinks = document.querySelectorAll('.auth-only');
  const guestLinks = document.querySelectorAll('.guest-only');
  const adminLink = document.querySelector('.admin-only') as HTMLElement;
  const myMoviesLink = document.querySelector('a[href="/views/mymovies"]')
    ?.parentElement as HTMLElement;

  const isLoggedIn = !!token;
  const user = token ? decodeJwtPayload(token) : null;

  authLinks.forEach((link) => {
    (link as HTMLElement).style.display = isLoggedIn ? 'inline' : 'none';
  });

  guestLinks.forEach((link) => {
    (link as HTMLElement).style.display = isLoggedIn ? 'none' : 'inline';
  });

  if (user && user.role === 'manager') {
    adminLink.style.display = 'inline';

    // Hide My Movies link for admin users
    if (myMoviesLink) {
      myMoviesLink.style.display = 'none';
    }
  } else {
    adminLink.style.display = 'none';
  }

  const logoutLink = document.querySelector('.logout-link') as HTMLElement;
  if (isLoggedIn && logoutLink) {
    logoutLink.style.display = 'inline';
  } else {
    logoutLink.style.display = 'none';
  }

  // Logout button
  const logoutBtn = document.getElementById('logoutBtn');
  if (logoutBtn) {
    logoutBtn.addEventListener('click', (e) => {
      e.preventDefault();
      document.cookie = 'token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 UTC;';
      window.location.href = '/views/login';
    });
  }
});
