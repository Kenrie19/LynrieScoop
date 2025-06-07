import { getCookie, decodeJwtPayload } from './cookies.js';

document.addEventListener('DOMContentLoaded', () => {
  const token = getCookie('token');
  if (!token) {
    window.location.href = '/views/login';
    return;
  }

  const user = decodeJwtPayload(token);
  if (!user || user.role !== 'manager') {
    alert('Access denied. Admins only.');
    window.location.href = '/views/login';
    return;
  }
});
