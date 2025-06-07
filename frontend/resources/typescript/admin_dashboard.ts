import { buildApiUrl } from './config.js';
import { getCookie, decodeJwtPayload } from './cookies.js';
import type { Chart as ChartJS } from 'chart.js';

declare global {
  interface Window {
    ticketChart?: ChartJS;
  }
}
declare const Chart: typeof ChartJS;

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

function redirectToLogin(): void {
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
      headers: { Authorization: `Bearer ${token}` },
    });

    if (!response.ok) throw new Error('Failed to load dashboard stats');

    const stats: DashboardStats = await response.json();
    renderDashboardStats(stats);

    await loadTicketChart(token);

    const updated = document.createElement('div');
    updated.classList.add('last-updated');
    updated.textContent = `Last updated: ${new Date(stats.last_updated).toLocaleString('nl-BE', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })}`;

    const chart = document.getElementById('ticketsChart');
    if (chart) chart.after(updated);
  } catch (error) {
    const errorDiv = document.getElementById('errorMessage');
    if (errorDiv) errorDiv.textContent = (error as Error).message;
  }

  const select = document.getElementById('timeGrouping') as HTMLSelectElement | null;
  if (select) {
    select.addEventListener('change', () => {
      loadTicketChart(token, select.value as GroupingOption);
    });
  }
});

function renderDashboardStats(stats: DashboardStats): void {
  const container = document.getElementById('statsGrid');
  if (!container) return;

  for (const [key, value] of Object.entries(stats)) {
    if (key === 'last_updated' || key === 'recent_revenue') continue;

    const card = document.createElement('div');
    card.classList.add('dashboard-card');

    const icon = document.createElement('div');
    icon.textContent = icons[key as keyof typeof icons] || 'ℹ️';
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
}

function formatKey(key: string): string {
  return key.replace(/_/g, ' ').replace(/\b\w/g, (char) => char.toUpperCase());
}

type GroupingOption = 'day' | 'week' | 'month' | 'year';

async function loadTicketChart(token: string, grouping: GroupingOption = 'day'): Promise<void> {
  const response = await fetch(buildApiUrl('/admin/admin/bookings?limit=1000'), {
    headers: { Authorization: `Bearer ${token}` },
  });

  if (!response.ok) {
    console.error('Failed to load bookings for chart');
    return;
  }

  const bookings: { showing_time?: string; start_time?: string }[] = await response.json();

  const counts: Record<string, number> = {};

  for (const booking of bookings) {
    const rawDate = booking.showing_time ?? booking.start_time;
    if (!rawDate) continue;

    const dateObj = new Date(rawDate);
    let key: string;

    switch (grouping) {
      case 'week': {
        const year = dateObj.getFullYear();
        const week = getISOWeekNumber(dateObj);
        key = `${year}-W${week}`;
        break;
      }
      case 'month':
        key = `${dateObj.getFullYear()}-${String(dateObj.getMonth() + 1).padStart(2, '0')}`;
        break;
      case 'year':
        key = `${dateObj.getFullYear()}`;
        break;
      case 'day':
      default:
        key = dateObj.toISOString().split('T')[0];
    }

    counts[key] = (counts[key] ?? 0) + 1;
  }

  const labels = Object.keys(counts).sort();
  const data = labels.map((label) => counts[label]);

  const ctx = document.getElementById('ticketsChart') as HTMLCanvasElement | null;
  if (!ctx) return;

  if (window.ticketChart) {
    window.ticketChart.destroy();
  }

  window.ticketChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [
        {
          label: 'Tickets Sold',
          data,
          backgroundColor: 'rgba(48, 213, 200, 0.5)',
          borderColor: 'rgba(48, 213, 200, 1)',
          borderWidth: 1,
        },
      ],
    },
    options: {
      responsive: true,
      plugins: {
        legend: {
          labels: { color: '#f1f1f1' },
        },
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: { color: '#f1f1f1' },
          title: { display: true, text: 'Tickets', color: '#f1f1f1' },
        },
        x: {
          ticks: { color: '#f1f1f1' },
          title: {
            display: true,
            text: grouping.charAt(0).toUpperCase() + grouping.slice(1),
            color: '#f1f1f1',
          },
        },
      },
    },
  });
}

function getISOWeekNumber(date: Date): number {
  const temp = new Date(date.valueOf());
  const day = (date.getDay() + 6) % 7;
  temp.setDate(temp.getDate() - day + 3);
  const firstThursday = new Date(temp.getFullYear(), 0, 4);
  const diff = (temp.getTime() - firstThursday.getTime()) / 86400000;
  return 1 + Math.floor(diff / 7);
}
