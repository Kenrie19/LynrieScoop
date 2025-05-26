import { setCookie } from './authHelpers.js';

async function login(email: string, password: string) {
  try {
    const res = await fetch('http://localhost:8000/auth/login', {
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
    window.location.href = '/views/mymovies';
  } catch (err) {
    showError('Invalid email or password');
  }
}

async function register(name: string, email: string, password: string) {
  try {
    const res = await fetch('http://localhost:8000/auth/register', {
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
    window.location.href = '/views/mymovies';
  } catch (err) {
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
