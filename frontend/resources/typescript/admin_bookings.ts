import { buildApiUrl } from './config.js';
import { getCookie, decodeJwtPayload } from './cookies.js';

interface Booking {
  id: string;
  user_id: string;
  showing_id: string;
  booking_number: string;
  status: string;
  total_price: number;
  created_at: string;
}

document.addEventListener('DOMContentLoaded', async () => {
  const token = getCookie('token');
  if (!token) return redirectToLogin();

  const user = decodeJwtPayload(token);
  if (!user || user.role !== 'manager') {
    alert('Access denied. Admins only.');
    return redirectToLogin();
  }

  try {
    const res = await fetch(buildApiUrl('/admin/admin/bookings?skip=0&limit=100'), {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (!res.ok) throw new Error('Failed to fetch bookings');

    const bookings: Booking[] = await res.json();
    const tableBody = document.querySelector('#bookingsTable tbody')!;

    bookings.forEach((booking) => {
      const row = document.createElement('tr');
      row.innerHTML = `
        <td>${booking.booking_number}</td>
        <td>${booking.user_id}</td>
        <td>${booking.showing_id}</td>
        <td>${booking.status}</td>
        <td>€${booking.total_price.toFixed(2)}</td>
        <td>${new Date(booking.created_at).toLocaleString()}</td>
      `;
      tableBody.appendChild(row);
    });
  } catch (err) {
    console.error(err);
    alert('Error loading bookings');
  }
});

function redirectToLogin() {
  window.location.href = '/views/login';
}
