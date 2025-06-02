import { getCookie } from './cookies.js';

declare global {
  interface Window {
    API_BASE_URL: string;
  }
}
const API_BASE_URL = window.API_BASE_URL || 'http://localhost:8000';

interface ShowingTicketInfo {
  showing_id: string;
  total_capacity: number;
  available_tickets: number;
  price: number;
  movie_title: string;
  start_time: string;
  end_time: string;
  room_name: string;
  movie_poster: string | null;
  movie_overview: string | null;
}

document.addEventListener('DOMContentLoaded', async () => {
  const showingId = getShowingIdFromURL();
  if (!showingId) {
    return showError('No showing ID provided in the URL.');
  }

  try {
    const showing = await fetchShowingInfo(showingId);
    updateReservationUI(showing);

    const form = document.getElementById('reservation-form') as HTMLFormElement;
    form.addEventListener('submit', (e) => handleReservationSubmit(e, showingId));
  } catch (error) {
    showError('Could not fetch showing data.');
    console.error(error);
  }
});

function getShowingIdFromURL(): string | null {
  const url = new URL(window.location.href);
  return url.searchParams.get('showing_id');
}

async function fetchShowingInfo(id: string): Promise<ShowingTicketInfo> {
  const res = await fetch(`${API_BASE_URL}/showings/showings/${id}/tickets`);
  if (!res.ok) {
    throw new Error('Error fetching showing.');
  }
  const data = await res.json();
  console.log('Showing data:', data);
  return data;
}

function updateReservationUI(showing: ShowingTicketInfo): void {
  const posterEl = document.getElementById('movie-poster') as HTMLImageElement | null;
  if (posterEl && showing.movie_poster) {
    posterEl.src = showing.movie_poster.startsWith('http')
      ? showing.movie_poster
      : `https://image.tmdb.org/t/p/w500${showing.movie_poster}`;
    posterEl.alt = showing.movie_title;
    posterEl.style.display = '';
  } else if (posterEl) {
    posterEl.style.display = 'none';
  }

  const movieTitleEl = document.getElementById('movie-title');
  if (movieTitleEl) movieTitleEl.textContent = showing.movie_title;

  const overviewEl = document.getElementById('movie-overview');
  if (overviewEl) overviewEl.textContent = showing.movie_overview || '';

  const cinemaNameEl = document.getElementById('cinema-name');
  if (cinemaNameEl) cinemaNameEl.textContent = showing.room_name;

  const dateEl = document.getElementById('showing-date');
  if (dateEl) dateEl.textContent = formatDate(showing.start_time);

  const timeEl = document.getElementById('showing-time');
  if (timeEl) timeEl.textContent = formatTime(showing.start_time);

  const ticketInput = document.getElementById('num-tickets') as HTMLInputElement | null;
  if (ticketInput) ticketInput.max = showing.available_tickets.toString();
}

function formatDate(dateTime: string): string {
  const date = new Date(dateTime);
  return date.toLocaleDateString('en-GB', { dateStyle: 'long' });
}

function formatTime(dateTime: string): string {
  const date = new Date(dateTime);
  return date.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' });
}

async function handleReservationSubmit(e: Event, showingId: string): Promise<void> {
  e.preventDefault();

  const token = getCookie('token');
  if (!token) {
    alert('You must be logged in to reserve a ticket.');
    window.location.href = '/views/login/index.html';
    return;
  }

  const ticketInput = document.getElementById('num-tickets') as HTMLInputElement | null;
  const numTickets = ticketInput ? parseInt(ticketInput.value, 10) : 0;
  const messageEl = document.getElementById('reservation-message');
  if (messageEl) messageEl.textContent = 'Reserving...';

  try {
    for (let i = 0; i < numTickets; i++) {
      const res = await fetch(
        `${API_BASE_URL}/bookings/bookings/create?screening_id=${showingId}`,
        {
          method: 'POST',
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Reservation failed.');
      }
    }

    if (messageEl) {
      messageEl.textContent = 'Reservation successful!';
      messageEl.style.color = 'green';
    }
  } catch (error) {
    if (messageEl) {
      const errMsg = error instanceof Error ? error.message : String(error);
      messageEl.textContent = `Error: ${errMsg}`;
      messageEl.style.color = 'red';
    }
  }
}

function showError(message: string): void {
  const el = document.getElementById('reservation-message');
  if (el) {
    el.textContent = message;
    el.style.color = 'red';
  }
}
