// import { getCookie } from './cookies.js';

// const urlParams = new URLSearchParams(window.location.search);
// const tmdbId = urlParams.get('tmdb_id');
// const form = document.getElementById('reservation-form') as HTMLFormElement | null;
// const messageDiv = document.getElementById('reservation-message') as HTMLElement | null;
// const cinemaNameSpan = document.getElementById('cinema-name') as HTMLElement | null;
// const movieTitleSpan = document.getElementById('movie-title') as HTMLElement | null;
// const showingTimeSpan = document.getElementById('showing-time') as HTMLElement | null;

// async function fetchScreeningsByTmdbId(tmdbId: string): Promise<any[]> {
//   const res = await fetch(`http://localhost:8000/showings/showings?movie_id=${tmdbId}`);
//   if (!res.ok) throw new Error('Kan screenings niet ophalen');
//   return await res.json();
// }

// async function fetchMovieDetails(movieId: number) {
//     const res = await fetch(`http://localhost:8000/movies/movies/${movieId}`);
//     if (!res.ok) throw new Error('Can not fetch movie details');
//     const movie = await res.json();
//     console.log('Fetched movie details:', movie);
//     return movie;
// }

// async function renderReservationInfo() {
//   if (!tmdbId) {
//     if (messageDiv) messageDiv.textContent = 'Geen geldige film geselecteerd.';
//     if (form) form.style.display = 'none';
//     return;
//   }

//   try {
//     const screenings = await fetchScreeningsByTmdbId(tmdbId);
//     const showing = selectNextAvailableScreening(screenings);

//     if (!showing) {
//       if (messageDiv) messageDiv.textContent = 'Geen actieve voorstellingen beschikbaar.';
//       if (form) form.style.display = 'none';
//       return;
//     }

//     // Vul info
//     if (cinemaNameSpan) cinemaNameSpan.textContent = showing.room_name || 'Onbekend';
//     if (showingTimeSpan) showingTimeSpan.textContent = new Date(showing.start_time).toLocaleString('nl-BE', {
//       hour: '2-digit',
//       minute: '2-digit',
//       day: '2-digit',
//       month: '2-digit',
//       year: 'numeric',
//     });

//     // Haal moviedetails op
//     const movie = await fetchMovieDetails(showing.movie_id);
//     if (movieTitleSpan) movieTitleSpan.textContent = movie.title || 'Onbekend';

//     // Sla showing ID op voor reservering
//     if (form) form.dataset.showingId = showing.id;

//   } catch (err) {
//     if (messageDiv) messageDiv.textContent = 'Kan reserveringsinfo niet laden.';
//     if (form) form.style.display = 'none';
//   }
// }

// if (form) {
//   form.addEventListener('submit', async (e) => {
//     e.preventDefault();
//     const numTickets = parseInt((document.getElementById('num-tickets') as HTMLInputElement).value, 10);
//     const token = getCookie('token');
//     if (!token) {
//       if (messageDiv) {
//         messageDiv.textContent = 'Je moet ingelogd zijn om te reserveren.';
//         messageDiv.className = 'error-message';
//       }
//       return;
//     }
//     try {
//       const res = await fetch('http://localhost:8000/bookings/reserve', {
//         method: 'POST',
//         headers: {
//           'Content-Type': 'application/json',
//           Authorization: `Bearer ${token}`,
//         },
//         body: JSON.stringify({ showing_id: form.dataset.showingId, num_tickets: numTickets }),
//       });
//       if (!res.ok) {
//         const err = await res.json();
//         if (messageDiv) {
//           messageDiv.textContent = err.detail || 'Reserveren mislukt.';
//           messageDiv.className = 'error-message';
//         }
//         return;
//       }
//       if (messageDiv) {
//         messageDiv.textContent = 'Reservering gelukt! Je tickets zijn geboekt.';
//         messageDiv.className = 'success-message';
//       }
//       form.reset();
//     } catch (err) {
//       if (messageDiv) {
//         messageDiv.textContent = 'Er is een fout opgetreden bij het reserveren.';
//         messageDiv.className = 'error-message';
//       }
//     }
//   });
// }

// renderReservationInfo();
