import { buildApiUrl } from './config.js';
import { getCookie, decodeJwtPayload } from './cookies.js';

interface DashboardStats {
  total_users: number;
  total_bookings: number;
  total_revenue: number;
  total_movies: number;
  total_showings: number;
  upcoming_showings: number;
  total_rooms: number;
  recent_bookings: number;
  recent_revenue: number;
  last_updated: string;
}

function redirectToLogin() {
  window.location.href = '/views/login';
}

const icons: Record<string, string> = {
  total_users: '👤',
  total_bookings: '🎟️',
  total_revenue: '💰',
  total_movies: '🎬',
  total_showings: '📅',
  upcoming_showings: '⏭️',
  total_rooms: '🏠',
  recent_bookings: '🕓',
  last_updated: '📅',
};

document.addEventListener('DOMContentLoaded', async () => {
  const token = getCookie('token');
  if (!token) return redirectToLogin();

  const user = decodeJwtPayload(token);
  if (!user || user.role !== 'manager') {
    alert('Access denied. Admins only.');
    return redirectToLogin();
  }

  try {
    const response = await fetch(buildApiUrl('/admin/admin/dashboard/stats'), {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (!response.ok) throw new Error('Failed to load dashboard stats');

    const stats: DashboardStats = await response.json();
    renderDashboardStats(stats);
  } catch (error) {
    const errorDiv = document.getElementById('errorMessage');
    if (errorDiv) errorDiv.textContent = (error as Error).message;
  }
});

function renderDashboardStats(stats: DashboardStats) {
  const container = document.getElementById('statsGrid');
  if (!container) return;

  const { last_updated } = stats;

  for (const [key, value] of Object.entries(stats)) {
    if (key === 'last_updated' || key === 'recent_revenue') continue;

    const card = document.createElement('div');
    card.classList.add('dashboard-card');

    const icon = document.createElement('div');
    icon.textContent = icons[key] || 'ℹ️';
    icon.classList.add('dashboard-icon');

    const label = document.createElement('h3');
    label.textContent = formatKey(key);

    const number = document.createElement('p');
    number.textContent = key.includes('revenue') ? `€${Number(value).toFixed(2)}` : `${value}`;

    card.appendChild(icon);
    card.appendChild(label);
    card.appendChild(number);
    container.appendChild(card);
  }

  const updated = document.createElement('div');
  updated.classList.add('last-updated');
  updated.textContent = `Last updated: ${new Date(last_updated).toLocaleString('nl-BE', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })}`;

  container.after(updated);
}

function formatKey(key: string): string {
  return key.replace(/_/g, ' ').replace(/\b\w/g, (char) => char.toUpperCase());
}
