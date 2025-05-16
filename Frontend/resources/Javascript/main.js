document.addEventListener('DOMContentLoaded', () => {
  const authOnlyLinks = document.querySelectorAll('.auth-only');
  const isLoggedIn = localStorage.getItem('loggedIn');

  authOnlyLinks.forEach(link => {
    link.style.display = isLoggedIn ? 'inline' : 'none';
  });
});
