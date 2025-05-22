interface Screening {
  id: string;
  movie_id: number;
  movie_title: string;
  start_time: string; // ISO string
  end_time: string;
  room: string;
  available_tickets: number;
  price: number;
}

let screenings: Screening[] = [];

async function fetchScreenings(): Promise<Screening[]> {
  const response = await fetch('http://localhost:8000/screenings/screenings');
  if (!response.ok) throw new Error('Failed to fetch screenings');
  return await response.json();
}

const filterBar = document.getElementById('filter-bar') as HTMLElement;
const moviesList = document.getElementById('movies-list') as HTMLElement;

const today = new Date();

function formatDate(date: Date): string {
  return date.toISOString().split('T')[0];
}

type DayOption = { label: string; value: string };
type DayOption = { label: string; value: string };

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
let selectedDay = 'today';

function renderFilterButtons(): void {
  filterBar.innerHTML = '';
  dayOptions.forEach((opt) => {
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
  [...filterBar.children].forEach((btn) => {
    btn.classList.toggle('active', btn instanceof HTMLElement && btn.dataset.value === selectedDay);
  });
}

function filterScreeningsBySelectedDay(): Screening[] {
  if (selectedDay === 'coming_soon') {
    // Coming soon: after the last day in dayOptions
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

async function renderMovies(): Promise<void> {
  moviesList.innerHTML = '';
  try {
    if (screenings.length === 0) {
      screenings = await fetchScreenings();
    }
    const filtered = filterScreeningsBySelectedDay();
    if (filtered.length === 0) {
      moviesList.innerHTML =
        "<p style='grid-column:1/-1; text-align:center; color:var(--light-grey);'>Geen films gevonden voor deze selectie.</p>";
      return;
    }
    // Group by movie_title and room
    const grouped: Record<string, { movie_title: string; room: string; times: string[] }> = {};
    filtered.forEach((screening) => {
      const key = `${screening.movie_title}__${screening.room}`;
      if (!grouped[key]) {
        grouped[key] = {
          movie_title: screening.movie_title,
          room: screening.room,
          times: [],
        };
      }
      grouped[key].times.push(
        new Date(screening.start_time).toLocaleTimeString([], {
          hour: '2-digit',
          minute: '2-digit',
        })
      );
    });
    // Use Object.keys and explicit typing to avoid Object.values error
    (Object.keys(grouped) as string[]).forEach((key) => {
      const group = grouped[key];
      const card = document.createElement('div');
      card.classList.add('movie-card');
      card.innerHTML = `
                <h3>${group.movie_title}</h3>
                <p><strong>Room:</strong> ${group.room}</p>
                <p><strong>Times:</strong> ${group.times.join(', ')}</p>
            `;
      moviesList.appendChild(card);
    });
  } catch {
    moviesList.innerHTML =
      "<p style='grid-column:1/-1; text-align:center; color:var(--light-grey);'>Failed to load screenings.</p>";
  }
}

// Initialize page
renderFilterButtons();
renderMovies();
