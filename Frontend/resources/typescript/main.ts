function getCookie(name: string): string | null {
  const cookies = document.cookie.split('; ');
  const found = cookies.find((row) => row.startsWith(name + '='));
  return found ? decodeURIComponent(found.split('=')[1]) : null;
}

document.addEventListener('DOMContentLoaded', () => {
  const token = getCookie('token');
  const authLinks = document.querySelectorAll('.auth-only');
  const guestLinks = document.querySelectorAll('.guest-only');

  authLinks.forEach((link) => {
    (link as HTMLElement).style.display = token ? 'inline' : 'none';
  });

  guestLinks.forEach((link) => {
    (link as HTMLElement).style.display = token ? 'none' : 'inline';
  });
});
