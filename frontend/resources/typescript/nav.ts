document.addEventListener('DOMContentLoaded', () => {
  const toggleBtn = document.getElementById('navToggle') as HTMLButtonElement | null;
  const navMenu = document.getElementById('navMenu') as HTMLUListElement | null;

  if (toggleBtn && navMenu) {
    toggleBtn.addEventListener('click', () => {
      navMenu.classList.toggle('active');
    });
  }
});
