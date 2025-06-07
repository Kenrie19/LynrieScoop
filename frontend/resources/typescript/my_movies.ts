import { getCookie } from './cookies.js';
import { buildApiUrl } from './config.js';

const FALLBACK_POSTER = '/resources/images/movie_mockup.jpg';

interface Booking {
  id: string;
  movie_title: string;
  poster_path: string;
  room_name: string;
  showing_time: string;
  total_price: number;
  status: string;
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
        const startTime = new Date(booking.showing_time);
        const isUpcoming = startTime > now;

        const card = document.createElement('div');
        card.className = 'movie-ticket';

        const poster = document.createElement('img');
        poster.src = booking.poster_path
          ? `https://image.tmdb.org/t/p/w500${booking.poster_path}`
          : FALLBACK_POSTER;
        poster.alt = booking.movie_title;
        card.appendChild(poster);

        const info = document.createElement('div');
        info.className = 'movie-info';

        const title = document.createElement('h3');
        title.textContent = booking.movie_title;

        const start = document.createElement('p');
        const strongStart = document.createElement('strong');
        strongStart.textContent = 'Start: ';
        start.appendChild(strongStart);
        start.append(startTime.toLocaleString());

        const room = document.createElement('p');
        const strongRoom = document.createElement('strong');
        strongRoom.textContent = 'Room: ';
        room.appendChild(strongRoom);
        room.append(booking.room_name);

        const price = document.createElement('p');
        const strongPrice = document.createElement('strong');
        strongPrice.textContent = 'Price: ';
        price.appendChild(strongPrice);
        price.append(`€${booking.total_price.toFixed(2)}`);

        info.appendChild(title);
        info.appendChild(start);
        info.appendChild(room);
        info.appendChild(price);

        if (isUpcoming) {
          const button = document.createElement('button');
          button.className = 'barcode-button';
          button.textContent = 'View Barcode';
          button.addEventListener('click', () => showBarcodePopup(booking.id));
          info.appendChild(button);
        }

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

//Barcode popup functie
function showBarcodePopup(bookingNumber: string) {
  const overlay = document.createElement('div');
  overlay.className = 'barcode-overlay';

  const popup = document.createElement('div');
  popup.className = 'barcode-popup';

  const title = document.createElement('h3');
  title.textContent = 'Your Ticket QR';

  const barcode = document.createElement('img');
  barcode.src = `https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${bookingNumber}`;
  barcode.alt = 'QR Code';

  const close = document.createElement('button');
  close.textContent = 'Close';
  close.addEventListener('click', () => {
    document.body.removeChild(overlay);
  });

  popup.appendChild(title);
  popup.appendChild(barcode);
  popup.appendChild(close);
  overlay.appendChild(popup);
  document.body.appendChild(overlay);
}
