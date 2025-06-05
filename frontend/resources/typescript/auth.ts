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
    if (user?.role === 'manager') {
      window.location.href = '/views/admin_screenings';
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
    window.location.href = '/views/my_movies';
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
});
