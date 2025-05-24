/**
 * Represents a movie screening event with details about time, location, and availability.
 * @interface
 */
interface Screening {
  /** Unique identifier for the screening */
  id: string;
  /** Identifier of the movie being screened */
  movie_id: number;
  /** Title of the movie being screened */
  movie_title: string;
  /** Start time of the screening in ISO format */
  start_time: string; // ISO string
  /** End time of the screening in ISO format */
  end_time: string;
  /** Room or theater where the screening takes place */
  room: string;
  /** Number of tickets still available for purchase */
  available_tickets: number;
  /** Price per ticket in the local currency */
  price: number;
}

/** Array to store all fetched screenings */
let screenings: Screening[] = [];

/**
 * Fetches movie screenings from the API.
 * @returns {Promise<Screening[]>} A promise that resolves to an array of screening objects
 * @throws {Error} When the network request fails
 */
async function fetchScreenings(): Promise<Screening[]> {
  const response = await fetch('http://localhost:8000/screenings/screenings');
  if (!response.ok) throw new Error('Failed to fetch screenings');
  return await response.json();
}

/** Reference to the filter bar element for date selection */
const filterBar = document.getElementById('filter-bar') as HTMLElement;
/** Reference to the container element for movie listings */
const moviesList = document.getElementById('movies-list') as HTMLElement;

/** Current date used for filtering screenings */
const today = new Date();

/**
 * Formats a Date object to YYYY-MM-DD string format
 * @param {Date} date - The date object to format
 * @returns {string} Date in YYYY-MM-DD format
 */
function formatDate(date: Date): string {
  return date.toISOString().split('T')[0];
}

/**
 * Represents a day option for the filter bar
 * @typedef {Object} DayOption
 * @property {string} label - Display label for the day option
 * @property {string} value - Value used for filtering screenings
 */
type DayOption = { label: string; value: string };

/**
 * Available day filter options for movie screenings
 */
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

/** Currently selected day filter value */
let selectedDay = 'today';

/**
 * Renders the day filter buttons in the filter bar
 */
/**
 * Renders the day filter buttons in the filter bar
 */
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

/**
 * Updates the active state of filter buttons based on the selected day
 */
function updateActiveButton(): void {
  [...filterBar.children].forEach((btn) => {
    btn.classList.toggle('active', btn instanceof HTMLElement && btn.dataset.value === selectedDay);
  });
}

/**
 * Filters screenings based on the selected day option
 * @returns {Screening[]} Array of screenings filtered by the selected day
 */
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

/**
 * Renders the list of movies based on the filtered screenings
 * Fetches screenings if needed and groups them by movie and room
 * @returns {Promise<void>}
 */
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
