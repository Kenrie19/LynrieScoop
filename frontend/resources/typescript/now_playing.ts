interface MovieDetail {
  /** UUID van de film in de database */
  id: string;
  /** TMDB ID van de film */
  tmdb_id: number;
  /** Titel van de film */
  title: string;
  /** Plot summary of description */
  overview: string | null;
  /** URL of path naar de poster */
  poster_path: string | null;
  /** URL of path naar de backdrop (optioneel) */
  backdrop_path?: string | null;
  /** Releasedatum in ISO formaat (optioneel) */
  release_date?: string | null;
  /** Duur in minuten (optioneel) */
  runtime?: number | null;
  /** Genres als lijst van strings (optioneel) */
  genres?: string[] | null;
  /** Gemiddelde rating (optioneel) */
  vote_average?: number | null;
  /** Aantal stemmen (optioneel) */
  vote_count?: number | null;
  /** Regisseur (optioneel) */
  director?: string | null;
  /** Cast als lijst van strings (optioneel) */
  cast?: string[] | null;
  /** Trailer URL (optioneel) */
  trailer_url?: string | null;
  /** Status van de film (optioneel) */
  status?: string | null;
}

interface Showing {
  id: string;
  movie_id: number;
  room_id: string | null;
  room_name: string | null;
  start_time: string;
  end_time: string | null;
  price: number;
}

type GroupedScreenings = {
  [date: string]: Showing[];
};

type DayOption = { label: string; value: string };

const filterBar = document.getElementById('filter-bar') as HTMLElement;
const moviesList = document.getElementById('movies-list') as HTMLElement;
const today = new Date();

const dayOptions: DayOption[] = [
  { label: 'Today', value: 'today' },
  { label: 'Tomorrow', value: 'tomorrow' },
  ...Array.from({ length: 4 }, (_, i) => {
    const d = new Date(today);
    d.setDate(d.getDate() + 2 + i);
    return { label: formatDate(d), value: formatDate(d) };
  }),
  { label: 'Coming Soon', value: 'coming_soon' },
];

let selectedDay = 'today';

document.addEventListener('DOMContentLoaded', async () => {
  renderFilterButtons();
  await renderMovies();
});

function formatDate(date: Date): string {
  return date.toISOString().split('T')[0];
}

function renderFilterButtons(): void {
  filterBar.innerHTML = '';
  dayOptions.forEach((opt) => {
    const btn = document.createElement('button');
    btn.textContent = opt.label;
    btn.dataset.value = opt.value;
    if (opt.value === selectedDay) btn.classList.add('active');
    btn.addEventListener('click', async () => {
      selectedDay = opt.value;
      updateActiveButton();
      await renderMovies();
    });
    filterBar.appendChild(btn);
  });
}

function updateActiveButton(): void {
  Array.from(filterBar.children).forEach((btn) => {
    btn.classList.toggle('active', btn instanceof HTMLElement && btn.dataset.value === selectedDay);
  });
}

async function renderMovies(): Promise<void> {
  moviesList.innerHTML = '';
  try {
    const nowPlaying: MovieDetail[] = await fetchNowPlaying();
    for (const movie of nowPlaying) {
      const screenings = await fetchScreenings(movie.tmdb_id);
      const filtered = filterScreeningsBySelectedDay(screenings);
      if (filtered.length === 0) continue;

      const grouped = groupAndSortByDate(filtered);
      const movieSection = document.createElement('div');
      movieSection.classList.add('movie-card');

      // Poster
      if (movie.poster_path) {
        const poster = document.createElement('img');
        poster.src = movie.poster_path;
        poster.alt = `${movie.title} poster`;
        poster.classList.add('movie-poster');
        movieSection.appendChild(poster);
      }

      // Title
      const title = document.createElement('h2');
      title.textContent = movie.title;
      movieSection.appendChild(title);

      // Screenings per date
      for (const [, screeningsOnDate] of Object.entries(grouped)) {
        const ul = document.createElement('ul');
        for (const s of screeningsOnDate) {
          const li = document.createElement('li');
          const time = new Date(s.start_time).toLocaleTimeString([], {
            hour: '2-digit',
            minute: '2-digit',
          });
          li.textContent = `Zaal ${s.room_name} - ${time} - €${s.price.toFixed(2)}`;
          ul.appendChild(li);
        }
        movieSection.appendChild(ul);
      }

      moviesList.appendChild(movieSection);
    }
  } catch (err) {
    console.error('Fout bij het laden van screenings:', err);
    moviesList.innerHTML =
      "<p style='grid-column:1/-1; text-align:center; color:var(--light-grey);'>Failed to load screenings.</p>";
  }
}

function filterScreeningsBySelectedDay(screenings: Showing[]): Showing[] {
  if (selectedDay === 'coming_soon') {
    const lastDay = dayOptions[dayOptions.length - 2].value;
    return screenings.filter((s) => s.start_time.split('T')[0] > lastDay);
  }
  let targetDate: string | null = null;
  if (selectedDay === 'today') targetDate = formatDate(today);
  else if (selectedDay === 'tomorrow') {
    const tmr = new Date(today);
    tmr.setDate(tmr.getDate() + 1);
    targetDate = formatDate(tmr);
  } else {
    targetDate = selectedDay;
  }
  return screenings.filter((s) => s.start_time.split('T')[0] === targetDate);
}

function groupAndSortByDate(screenings: Showing[]): GroupedScreenings {
  const grouped: GroupedScreenings = {};
  for (const screening of screenings) {
    const date = screening.start_time.split('T')[0];
    if (!grouped[date]) grouped[date] = [];
    grouped[date].push(screening);
  }
  const sortedGrouped: GroupedScreenings = {};
  const sortedDates = Object.keys(grouped).sort().slice(0, 5);
  for (const date of sortedDates) {
    sortedGrouped[date] = grouped[date].sort(
      (a, b) => new Date(a.start_time).getTime() - new Date(b.start_time).getTime()
    );
  }
  return sortedGrouped;
}

async function fetchNowPlaying(): Promise<MovieDetail[]> {
  const res = await fetch('http://localhost:8000/showings/showings/now-playing');
  if (!res.ok) throw new Error('Failed to fetch now playing movies');
  const data = await res.json();
  console.log('Now Playing Movies:', data);
  return data;
}

async function fetchScreenings(movieId: number): Promise<Showing[]> {
  const res = await fetch(`http://localhost:8000/showings/showings?movie_id=${movieId}`);
  if (!res.ok) throw new Error(`Failed to fetch screenings for movie ${movieId}`);
  const data = await res.json();
  console.log('The data fetched from the API:', data);
  return data;
}
