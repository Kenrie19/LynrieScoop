/**
 * Represents a movie ticket with booking details.
 * @interface
 */
interface MovieTicket {
  /** The title of the movie */
  title: string;
  /** URL to the movie poster image */
  posterUrl: string;
  /** Date of the screening in YYYY-MM-DD format */
  date: string;
  /** Time of the screening in HH:MM format */
  time: string;
  /** Room or theater where the screening takes place */
  room: string;
  /** Comma-separated list of seat numbers */
  seats: string;
  /** Whether this is an upcoming screening (true) or a past screening (false) */
  isUpcoming: boolean;
}

/** Default path to the movie poster image used for mockup tickets */
const posterPath = '/resources/images/movie_mockup.jpg';

/**
 * Sample movie tickets for demonstration purposes
 */
const movieTickets: MovieTicket[] = [
  {
    title: 'Dune: Part Two',
    posterUrl: posterPath,
    date: '2025-06-01',
    time: '20:30',
    room: 'Zaal 1',
    seats: 'B3, B4',
    isUpcoming: true,
  },
  {
    title: 'Oppenheimer',
    posterUrl: posterPath,
    date: '2025-06-03',
    time: '18:00',
    room: 'Zaal 2',
    seats: 'C1, C2, C3',
    isUpcoming: true,
  },
  {
    title: 'Barbie',
    posterUrl: posterPath,
    date: '2025-05-10',
    time: '19:00',
    room: 'Zaal 3',
    seats: 'A5, A6',
    isUpcoming: false,
  },
  {
    title: 'The Batman',
    posterUrl: posterPath,
    date: '2025-05-08',
    time: '21:30',
    room: 'Zaal 1',
    seats: 'D1, D2',
    isUpcoming: false,
  },
  {
    title: 'Interstellar',
    posterUrl: posterPath,
    date: '2025-06-07',
    time: '20:00',
    room: 'Zaal 4',
    seats: 'E4, E5',
    isUpcoming: true,
  },
  {
    title: 'Avatar: The Way of Water',
    posterUrl: posterPath,
    date: '2025-05-01',
    time: '17:30',
    room: 'Zaal 2',
    seats: 'F1, F2',
    isUpcoming: false,
  },
];

/**
 * Creates an HTML element representing a movie ticket card
 * @param {MovieTicket} ticket - The ticket data to display
 * @returns {HTMLElement} A div element containing the formatted ticket information
 */
function createMovieTicketCard(ticket: MovieTicket): HTMLElement {
  const card = document.createElement('div');
  card.classList.add('movie-ticket');

  card.innerHTML = `
    <img src="${ticket.posterUrl}" alt="${ticket.title} poster">
    <div class="movie-info">
      <h3>${ticket.title}</h3>
      <p><strong>Datum:</strong> ${ticket.date}</p>
      <p><strong>Uur:</strong> ${ticket.time}</p>
      <p><strong>Zaal:</strong> ${ticket.room}</p>
      <p><strong>Plaatsen:</strong> ${ticket.seats}</p>
      ${ticket.isUpcoming ? `<button class="barcode-button">Bekijk Barcode</button>` : ''}
    </div>
  `;

  return card;
}

/**
 * Renders all movie tickets, separating them into upcoming and watched sections
 */
function renderMovieTickets() {
  const upcomingContainer = document.querySelector('.upcoming-movies') as HTMLElement;
  const watchedContainer = document.querySelector('.watched-movies') as HTMLElement;

  const upcomingList = document.createElement('div');
  upcomingList.classList.add('movie-ticket-list');

  const watchedList = document.createElement('div');
  watchedList.classList.add('movie-ticket-list');

  upcomingContainer.innerHTML = `<h2>Booked movies</h2>`;
  watchedContainer.innerHTML = `<h2>Previous movies</h2>`;

  movieTickets.forEach((ticket) => {
    const card = createMovieTicketCard(ticket);
    if (ticket.isUpcoming) {
      upcomingList.appendChild(card);
    } else {
      watchedList.appendChild(card);
    }
  });

  upcomingContainer.appendChild(upcomingList);
  watchedContainer.appendChild(watchedList);
}

/**
 * Initialize the page content when the DOM is fully loaded
 */
document.addEventListener('DOMContentLoaded', renderMovieTickets);
