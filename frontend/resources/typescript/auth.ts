import { setCookie, decodeJwtPayload } from './cookies.js';
import { buildApiUrl } from './config.js';

async function login(email: string, password: string) {
  try {
    const res = await fetch(buildApiUrl('/auth/login'), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password }),
    });

    if (!res.ok) {
      throw new Error('Login failed');
    }

    const data = await res.json();
    setCookie('token', data.access_token, 1);

    const user = decodeJwtPayload(data.access_token);

    const storedNext = sessionStorage.getItem('next');
    const urlParams = new URLSearchParams(window.location.search);
    const next = urlParams.get('next') || storedNext;

    if (next) {
      sessionStorage.removeItem('next'); // Clear session storage if next is used
      window.location.href = next;
      return;
    }

    if (user?.role === 'manager') {
      window.location.href = '/views/admin';
    } else {
      window.location.href = '/views/my_movies';
    }
  } catch {
    showError('Invalid email or password');
  }
}

async function register(name: string, email: string, password: string) {
  try {
    const res = await fetch(buildApiUrl('/auth/register'), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ name, email, password }),
    });

    if (!res.ok) {
      throw new Error('Registration failed');
    }

    const data = await res.json();
    setCookie('token', data.access_token, 1);

    const storedNext = sessionStorage.getItem('next');
    const urlParams = new URLSearchParams(window.location.search);
    const next = urlParams.get('next') || storedNext;

    if (next) {
      window.location.href = next;
    } else {
      window.location.href = '/views/my_movies';
    }
  } catch {
    showError('Registration failed. Email might be already in use.');
  }
}

function showError(message: string) {
  const errorElement = document.getElementById('error');
  if (errorElement) {
    errorElement.textContent = message;
    errorElement.style.display = 'block';
  }
}

// Event listeners
document.addEventListener('DOMContentLoaded', () => {
  const loginForm = document.getElementById('loginForm') as HTMLFormElement;
  if (loginForm) {
    loginForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const email = (document.getElementById('email') as HTMLInputElement).value;
      const password = (document.getElementById('password') as HTMLInputElement).value;
      login(email, password);
    });
  }

  const registerForm = document.getElementById('registerForm') as HTMLFormElement;
  if (registerForm) {
    registerForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const name = (document.getElementById('name') as HTMLInputElement).value;
      const email = (document.getElementById('email') as HTMLInputElement).value;
      const password = (document.getElementById('password') as HTMLInputElement).value;
      register(name, email, password);
    });
  }
  const registerLink = document.getElementById('register-link') as HTMLAnchorElement;
  if (registerLink) {
    registerLink.addEventListener('click', (e) => {
      e.preventDefault();
      const urlParams = new URLSearchParams(window.location.search);
      const next = urlParams.get('next');
      const registerUrl = next
        ? `/views/register?next=${encodeURIComponent(next)}`
        : `/views/register`;
      window.location.href = registerUrl;
    });
  }
  const backToLogin = document.getElementById('back-to-login') as HTMLAnchorElement;
  if (backToLogin) {
    backToLogin.addEventListener('click', (e) => {
      e.preventDefault();
      const storedNext = sessionStorage.getItem('next');
      const loginUrl = storedNext
        ? `/views/login/index.html?next=${encodeURIComponent(storedNext)}`
        : `/views/login/index.html`;
      window.location.href = loginUrl;
    });
  }
});
