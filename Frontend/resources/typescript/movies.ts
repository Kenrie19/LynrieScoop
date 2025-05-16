interface Movie {
  id: number;
  title: string;
  release_date: string; // YYYY-MM-DD
  poster_path: string;
}

const movies: Movie[] = [
  { id: 1, title: "Avengers: Endgame", release_date: "2025-05-16", poster_path: "https://via.placeholder.com/300x450?text=Avengers" },
  { id: 2, title: "The Batman", release_date: "2025-05-17", poster_path: "https://via.placeholder.com/300x450?text=Batman" },
  { id: 3, title: "Dune", release_date: "2025-05-20", poster_path: "https://via.placeholder.com/300x450?text=Dune" },
  { id: 4, title: "Avatar 3", release_date: "2025-06-10", poster_path: "https://via.placeholder.com/300x450?text=Avatar+3" },
  { id: 5, title: "Fantastic Beasts", release_date: "2025-06-15", poster_path: "https://via.placeholder.com/300x450?text=Fantastic+Beasts" },
  { id: 6, title: "Spider-Man: No Way Home", release_date: "2025-05-18", poster_path: "https://via.placeholder.com/300x450?text=Spider-Man" },
];

const filterBar = document.getElementById('filter-bar') as HTMLElement;
const moviesList = document.getElementById('movies-list') as HTMLElement;

const today = new Date();

function formatDate(date: Date): string {
  return date.toISOString().split('T')[0];
}

type DayOption = { label: string; value: string; };

const dayOptions: DayOption[] = [
  { label: "Vandaag", value: "today" },
  { label: "Morgen", value: "tomorrow" },
  ...Array.from({ length: 10 }, (_, i) => {
    const d = new Date(today);
    d.setDate(d.getDate() + 2 + i);
    return { label: formatDate(d), value: formatDate(d) };
  }),
  { label: "Coming Soon", value: "coming_soon" }
];

let selectedDay = "today";

function renderFilterButtons(): void {
  filterBar.innerHTML = "";
  dayOptions.forEach(opt => {
    const btn = document.createElement('button');
    btn.textContent = opt.label;
    btn.dataset.value = opt.value;
    if (opt.value === selectedDay) btn.classList.add('active');
    btn.addEventListener('click', () => {
      selectedDay = opt.value;
      updateActiveButton();
      renderMovies();
    });
    filterBar.appendChild(btn);
  });
}

function updateActiveButton(): void {
  [...filterBar.children].forEach(btn => {
    btn.classList.toggle('active', btn instanceof HTMLElement && btn.dataset.value === selectedDay);
  });
}

function filterMovies(): Movie[] {
  if (selectedDay === "coming_soon") {
    const dateLimit = new Date(today);
    dateLimit.setDate(dateLimit.getDate() + 12);
    return movies.filter(m => new Date(m.release_date) > dateLimit);
  }

  let targetDate: string | null = null;
  if (selectedDay === "today") targetDate = formatDate(today);
  else if (selectedDay === "tomorrow") {
    const tmr = new Date(today);
    tmr.setDate(tmr.getDate() + 1);
    targetDate = formatDate(tmr);
  } else {
    targetDate = selectedDay; // is een datum string
  }

  return movies.filter(m => m.release_date === targetDate);
}

function renderMovies(): void {
  moviesList.innerHTML = "";

  const filtered = filterMovies();

  if (filtered.length === 0) {
    moviesList.innerHTML = "<p style='grid-column:1/-1; text-align:center; color:var(--light-grey);'>Geen films gevonden voor deze selectie.</p>";
    return;
  }

  filtered.forEach(movie => {
    const card = document.createElement('div');
    card.classList.add('movie-card');

    card.innerHTML = `
      <img src="${movie.poster_path}" alt="${movie.title} poster" />
      <h3>${movie.title}</h3>
      <p style="text-align:center; color: var(--light-grey); font-size: 0.9rem;">Speelt op: ${movie.release_date}</p>
    `;

    moviesList.appendChild(card);
  });
}

// Initialize page
renderFilterButtons();
renderMovies();
