import { getCookie } from './cookies.js';
import { buildApiUrl } from './config.js';

interface Booking {
  movie: {
    title: string;
    poster_path: string;
  };
  screening: {
    start_time: string;
    end_time: string;
    room: { name: string };
    price: number;
  };
}

document.addEventListener('DOMContentLoaded', () => {
  const token = getCookie('token');
  if (!token) {
    window.location.href = '/views/login';
    return;
  }

  fetch(buildApiUrl('/bookings/bookings/my-bookings'), {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  })
    .then((res) => {
      if (!res.ok) throw new Error('Failed to fetch bookings');
      return res.json();
    })
    .then((bookings: Booking[]) => {
      const upcomingContainer = document.getElementById('upcoming-list')!;
      const watchedContainer = document.getElementById('watched-list')!;
      const now = new Date();

      bookings.forEach((booking) => {
        const startTime = new Date(booking.screening.start_time);
        const isUpcoming = startTime > now;

        const card = document.createElement('div');
        card.className = 'movie-ticket';

        const poster = document.createElement('img');
        poster.src = booking.movie.poster_path
          ? `https://image.tmdb.org/t/p/w500${booking.movie.poster_path}`
          : '/resources/images/placeholder.jpg';
        poster.alt = booking.movie.title;

        const info = document.createElement('div');
        info.className = 'movie-info';
        info.innerHTML = `
          <h3>${booking.movie.title}</h3>
          <p><strong>Start:</strong> ${startTime.toLocaleString()}</p>
          <p><strong>Room:</strong> ${booking.screening.room.name}</p>
          <p><strong>Price:</strong> €${booking.screening.price.toFixed(2)}</p>
          <button class="barcode-button">View Barcode</button>
        `;

        card.appendChild(poster);
        card.appendChild(info);

        if (isUpcoming) {
          upcomingContainer.appendChild(card);
        } else {
          watchedContainer.appendChild(card);
        }
      });
    })
    .catch((err) => {
      console.error('Error loading bookings:', err);
    });
});
