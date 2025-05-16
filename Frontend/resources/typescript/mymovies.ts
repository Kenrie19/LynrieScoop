interface MovieTicket {
  title: string;
  posterUrl: string;
  date: string;
  time: string;
  room: string;
  seats: string;
  isUpcoming: boolean;
}

const posterPath = "/resources/images/movie_mockup.jpg";

const movieTickets: MovieTicket[] = [
  {
    title: "Dune: Part Two",
    posterUrl: posterPath,
    date: "2025-06-01",
    time: "20:30",
    room: "Zaal 1",
    seats: "B3, B4",
    isUpcoming: true,
  },
  {
    title: "Oppenheimer",
    posterUrl: posterPath,
    date: "2025-06-03",
    time: "18:00",
    room: "Zaal 2",
    seats: "C1, C2, C3",
    isUpcoming: true,
  },
  {
    title: "Barbie",
    posterUrl: posterPath,
    date: "2025-05-10",
    time: "19:00",
    room: "Zaal 3",
    seats: "A5, A6",
    isUpcoming: false,
  },
  {
    title: "The Batman",
    posterUrl: posterPath,
    date: "2025-05-08",
    time: "21:30",
    room: "Zaal 1",
    seats: "D1, D2",
    isUpcoming: false,
  },
  {
    title: "Interstellar",
    posterUrl: posterPath,
    date: "2025-06-07",
    time: "20:00",
    room: "Zaal 4",
    seats: "E4, E5",
    isUpcoming: true,
  },
  {
    title: "Avatar: The Way of Water",
    posterUrl: posterPath,
    date: "2025-05-01",
    time: "17:30",
    room: "Zaal 2",
    seats: "F1, F2",
    isUpcoming: false,
  },
];

function createMovieTicketCard(ticket: MovieTicket): HTMLElement {
  const card = document.createElement("div");
  card.classList.add("movie-ticket");

  card.innerHTML = `
    <img src="${ticket.posterUrl}" alt="${ticket.title} poster">
    <div class="movie-info">
      <h3>${ticket.title}</h3>
      <p><strong>Datum:</strong> ${ticket.date}</p>
      <p><strong>Uur:</strong> ${ticket.time}</p>
      <p><strong>Zaal:</strong> ${ticket.room}</p>
      <p><strong>Plaatsen:</strong> ${ticket.seats}</p>
      ${ticket.isUpcoming ? `<button class="barcode-button">Bekijk Barcode</button>` : ""}
    </div>
  `;

  return card;
}

function renderMovieTickets() {
  const upcomingContainer = document.querySelector(".upcoming-movies") as HTMLElement;
  const watchedContainer = document.querySelector(".watched-movies") as HTMLElement;

  const upcomingList = document.createElement("div");
  upcomingList.classList.add("movie-ticket-list");

  const watchedList = document.createElement("div");
  watchedList.classList.add("movie-ticket-list");

  upcomingContainer.innerHTML = `<h2>Booked movies</h2>`;
  watchedContainer.innerHTML = `<h2>Previous movies</h2>`;

  movieTickets.forEach(ticket => {
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

document.addEventListener("DOMContentLoaded", renderMovieTickets);
