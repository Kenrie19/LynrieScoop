import { getCookie } from './cookies.js';
import { buildApiUrl } from './config.js';

interface MovieDetail {
  id: string;
  tmdb_id: number;
  title: string;
  overview: string | null;
  poster_path: string | null;
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
const FALLBACK_POSTER = '/resources/images/movie_mockup.jpg';
const today = new Date();

const dayOptions: DayOption[] = [
  { label: 'Today', value: 'today' },
  { label: 'Tomorrow', value: 'tomorrow' },
  ...Array.from({ length: 4 }, (_, i) => {
    const d = new Date(today);
    d.setDate(d.getDate() + 2 + i);
    return { label: formatDate(d), value: formatDate(d) };
  }),
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

    const moviesWithFirstScreening = await Promise.all(
      nowPlaying.map(async (movie) => {
        const screenings = await fetchScreenings(movie.tmdb_id);
        const filtered = filterScreeningsBySelectedDay(screenings);
        const firstScreening = filtered.length > 0 ? filtered[0].start_time : null;
        return { movie, screenings, filtered, firstScreening };
      })
    );

    moviesWithFirstScreening.sort((a, b) => {
      if (!a.firstScreening && !b.firstScreening) return 0;
      if (!a.firstScreening) return 1;
      if (!b.firstScreening) return -1;
      return new Date(a.firstScreening).getTime() - new Date(b.firstScreening).getTime();
    });

    for (const { movie, filtered } of moviesWithFirstScreening) {
      if (filtered.length === 0) continue;

      const movieSection = document.createElement('div');
      movieSection.classList.add('movie-card');

      // Poster
      const posterButton = document.createElement('button');
      posterButton.classList.add('poster-btn');
      posterButton.addEventListener('click', (e) => {
        e.stopPropagation();
        window.location.href = `/views/movie_details/index.html?id=${movie.tmdb_id}`;
      });

      const poster = document.createElement('img');
      poster.src = movie.poster_path
        ? `https://image.tmdb.org/t/p/w500${movie.poster_path}`
        : FALLBACK_POSTER;
      poster.alt = `${movie.title} poster`;
      poster.classList.add('movie-poster');
      posterButton.appendChild(poster);

      // Info wrapper
      const infoWrapper = document.createElement('div');
      infoWrapper.classList.add('movie-info-wrapper');

      const title = document.createElement('h2');
      title.classList.add('movie-title');
      title.textContent = movie.title;
      infoWrapper.appendChild(title);

      // Overview
      if (movie.overview) {
        const overview = document.createElement('p');
        overview.classList.add('movie-overview');
        overview.textContent = movie.overview;
        infoWrapper.appendChild(overview);
      }

      // Group screenings
      const grouped = groupAndSortByDate(filtered);
      for (const [, screeningsOnDate] of Object.entries(grouped)) {
        const timeContainer = document.createElement('div');
        timeContainer.classList.add('screening-times');

        screeningsOnDate.forEach((s) => {
          const screeningItem = document.createElement('div');
          screeningItem.classList.add('screening-time-item-unique');

          const roomSpan = document.createElement('span');
          roomSpan.classList.add('screening-room');
          roomSpan.textContent = s.room_name || '';

          const timeButton = document.createElement('button');
          const time = new Date(s.start_time).toLocaleTimeString([], {
            hour: '2-digit',
            minute: '2-digit',
          });
          timeButton.textContent = time;
          timeButton.classList.add('screening-time-btn');

          const isToday = selectedDay === 'today';
          const screeningDate = new Date(s.start_time);
          const now = new Date();
          if (isToday && screeningDate < now) {
            timeButton.disabled = true;
          } else {
            timeButton.addEventListener('click', (e) => {
              e.stopPropagation();
              const token = getCookie('token');
              if (!token) {
                sessionStorage.setItem(
                  'next',
                  `/views/ticket_reservation/index.html?showing_id=${s.id}`
                );
                window.location.href = `/views/login/index.html`;
                return;
              }
              window.location.href = `/views/ticket_reservation/index.html?showing_id=${s.id}`;
            });
          }

          screeningItem.appendChild(roomSpan);
          screeningItem.appendChild(timeButton);
          timeContainer.appendChild(screeningItem);
        });

        infoWrapper.appendChild(timeContainer);
      }

      movieSection.appendChild(posterButton);
      movieSection.appendChild(infoWrapper);
      moviesList.appendChild(movieSection);
    }
  } catch {
    moviesList.innerHTML =
      "<p style='text-align:center; color:var(--light-grey);'>Failed to load screenings.</p>";
  }
}

function filterScreeningsBySelectedDay(screenings: Showing[]): Showing[] {
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
  const res = await fetch(buildApiUrl('/showings/showings/now-playing'));
  if (!res.ok) throw new Error('Failed to fetch now playing movies');
  return res.json();
}

async function fetchScreenings(movieId: number): Promise<Showing[]> {
  const res = await fetch(buildApiUrl(`/showings/showings?movie_id=${movieId}`));
  if (!res.ok) throw new Error(`Failed to fetch screenings for movie ${movieId}`);
  return res.json();
}
