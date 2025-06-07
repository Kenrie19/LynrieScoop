// This script handles the ticket reservation page logic for a movie showing.
// It fetches showing info, updates the UI, manages ticket input, and handles real-time ticket updates via MQTT.
// It also processes the reservation form, enforces a max of 10 tickets per user, and redirects to the user's tickets after booking.

import { getCookie } from './cookies.js';

declare global {
  interface Window {
    API_BASE_URL: string;
    Paho: unknown;
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

// --- Main event: On DOMContentLoaded, fetch showing info and set up the reservation form ---
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

// --- Fetch showing info from the backend API ---
async function fetchShowingInfo(id: string): Promise<ShowingTicketInfo> {
  const res = await fetch(`${API_BASE_URL}/showings/showings/${id}/tickets`);
  if (!res.ok) {
    throw new Error('Error fetching showing.');
  }
  const data = await res.json();
  console.log('Showing data:', data);
  return data;
}

// MQTT setup for real-time updates
// This function sets up the MQTT client to listen for updates on ticket availability
// It uses the global Paho client from the window object, which is expected to be loaded from a CDN.
function setupMqttRealtime(showingId: string) {
  // Use the global Paho client from the window object
  type PahoClientType = {
    onConnectionLost: (() => void) | null;
    onMessageArrived: ((msg: { destinationName: string; payloadString: string }) => void) | null;
    connect: (options: { onSuccess: () => void; useSSL: boolean }) => void;
    subscribe: (topic: string) => void;
  };
  // Paho from CDN has the Client property directly
  const PahoNS = window.Paho as {
    Client: new (host: string, port: number, path: string, clientId: string) => PahoClientType;
  };
  if (!PahoNS || !PahoNS.Client) {
    console.warn('MQTT client not loaded.');
    return;
  }
  const host = 'localhost';
  const port = 9001;
  const path = '/';
  const clientId = 'web-' + Math.random();
  const client = new PahoNS.Client(host, port, path, clientId);
  client.onConnectionLost = () => {
    const ticketInput = document.getElementById('num-tickets') as HTMLInputElement | null;
    if (ticketInput) ticketInput.disabled = true;
    const msg = document.getElementById('reservation-message');
    if (msg) msg.textContent = 'Connection to server lost.';
  };
  client.onMessageArrived = (msg: { destinationName: string; payloadString: string }) => {
    if (msg.destinationName === `screenings/${showingId}/update`) {
      const payload = JSON.parse(msg.payloadString);
      const ticketInput = document.getElementById('num-tickets') as HTMLInputElement | null;
      if (ticketInput) ticketInput.max = payload.available_tickets.toString();
      showAvailableTicketsDiv(payload.available_tickets); // update all UI aspects
    }
  };
  client.connect({
    onSuccess: () => {
      client.subscribe(`screenings/${showingId}/update`);
    },
    useSSL: false,
  });
}

// --- Show or update the available tickets div above the reservation form ---
function showAvailableTicketsDiv(count: number) {
  let availableDiv = document.getElementById('available-tickets');
  if (!availableDiv) {
    availableDiv = document.createElement('div');
    availableDiv.id = 'available-tickets';
    availableDiv.style.textAlign = 'center';
    const form = document.getElementById('reservation-form');
    form?.parentElement?.insertBefore(availableDiv, form);
  }
  if (count <= 0) {
    availableDiv.textContent = 'Fully booked';
    availableDiv.style.color = 'red';
    // Disable the reserve button
    const reserveBtn = document.querySelector(
      '#reservation-form button[type="submit"]'
    ) as HTMLButtonElement | null;
    if (reserveBtn) reserveBtn.disabled = true;
    // Also disable the ticket input
    const ticketInput = document.getElementById('num-tickets') as HTMLInputElement | null;
    if (ticketInput) ticketInput.disabled = true;
  } else {
    availableDiv.textContent = `Available tickets: ${count}`;
    availableDiv.style.color = '';
    // Enable the reserve button
    const reserveBtn = document.querySelector(
      '#reservation-form button[type="submit"]'
    ) as HTMLButtonElement | null;
    if (reserveBtn) reserveBtn.disabled = false;
    // Enable the ticket input
    const ticketInput = document.getElementById('num-tickets') as HTMLInputElement | null;
    if (ticketInput) ticketInput.disabled = false;
  }
}

// --- Update the reservation UI with showing details and ticket limits ---
function updateReservationUI(showing: ShowingTicketInfo): void {
  const posterEl = document.getElementById('movie-poster') as HTMLImageElement | null;
  const FALLBACK_POSTER = '/resources/images/movie_mockup.jpg';

  if (posterEl) {
    if (showing.movie_poster) {
      posterEl.src = showing.movie_poster.startsWith('http')
        ? showing.movie_poster
        : `https://image.tmdb.org/t/p/w500${showing.movie_poster}`;
    } else {
      posterEl.src = FALLBACK_POSTER;
    }
    posterEl.alt = showing.movie_title;
    posterEl.style.display = '';
  }

  const movieTitleEl = document.getElementById('movie-title');
  if (movieTitleEl) movieTitleEl.textContent = showing.movie_title;

  const cinemaNameEl = document.getElementById('cinema-name');
  if (cinemaNameEl) cinemaNameEl.textContent = showing.room_name;

  // Show price
  const priceEl = document.getElementById('showing-price');
  if (priceEl) priceEl.textContent = `€${showing.price.toFixed(2)}`;

  const dateEl = document.getElementById('showing-date');
  if (dateEl) dateEl.textContent = formatDate(showing.start_time);

  const timeEl = document.getElementById('showing-time');
  if (timeEl) timeEl.textContent = formatTime(showing.start_time);

  const ticketInput = document.getElementById('num-tickets') as HTMLInputElement | null;
  if (ticketInput) ticketInput.max = Math.min(10, showing.available_tickets).toString();
  showAvailableTicketsDiv(showing.available_tickets);
  setupMqttRealtime(showing.showing_id);
}

function formatDate(dateTime: string): string {
  const date = new Date(dateTime);
  return date.toLocaleDateString('en-GB', { dateStyle: 'long' });
}

function formatTime(dateTime: string): string {
  const date = new Date(dateTime);
  return date.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' });
}

// --- Handle reservation form submission, enforce max 10 tickets, and redirect on success ---
async function handleReservationSubmit(e: Event, showingId: string): Promise<void> {
  e.preventDefault();

  const token = getCookie('token');
  if (!token) {
    alert('You must be logged in to reserve a ticket.');
    window.location.href = '/views/login/index.html';
    return;
  }

  const ticketInput = document.getElementById('num-tickets') as HTMLInputElement | null;
  let numTickets = ticketInput ? parseInt(ticketInput.value, 10) : 0;
  if (numTickets > 10) numTickets = 10;
  if (numTickets < 1) numTickets = 1;
  if (ticketInput) ticketInput.value = numTickets.toString();
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
    setTimeout(() => {
      window.location.href = '/views/my_movies/index.html';
    }, 1000);
  } catch (error) {
    if (messageEl) {
      const errMsg = error instanceof Error ? error.message : String(error);
      messageEl.textContent = `Error: ${errMsg}`;
      messageEl.style.color = 'red';
    }
  }
}

// --- Show error messages in the reservation-message element ---
function showError(message: string): void {
  const el = document.getElementById('reservation-message');
  if (el) {
    el.textContent = message;
    el.style.color = 'red';
  }
}
