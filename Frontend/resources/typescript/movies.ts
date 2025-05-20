interface Movie {
    id: number;
    title: string;
    release_date: string; // YYYY-MM-DD
    poster_path: string;
}

const movies: Movie[] = [
    {
        id: 1,
        title: 'Avengers: Endgame',
        release_date: '2025-05-16',
        poster_path: 'https://via.placeholder.com/300x450?text=Avengers',
    },
    {
        id: 2,
        title: 'The Batman',
        release_date: '2025-05-17',
        poster_path: 'https://via.placeholder.com/300x450?text=Batman',
    },
    {
        id: 3,
        title: 'Dune',
        release_date: '2025-05-20',
        poster_path: 'https://via.placeholder.com/300x450?text=Dune',
    },
    {
        id: 4,
        title: 'Avatar 3',
        release_date: '2025-06-10',
        poster_path: 'https://via.placeholder.com/300x450?text=Avatar+3',
    },
    {
        id: 5,
        title: 'Fantastic Beasts',
        release_date: '2025-06-15',
        poster_path:
            'https://via.placeholder.com/300x450?text=Fantastic+Beasts',
    },
    {
        id: 6,
        title: 'Spider-Man: No Way Home',
        release_date: '2025-05-18',
        poster_path: 'https://via.placeholder.com/300x450?text=Spider-Man',
    },
];

const filterBar = document.getElementById('filter-bar') as HTMLElement;
const moviesList = document.getElementById('movies-list') as HTMLElement;

const today = new Date();

function formatDate(date: Date): string {
    return date.toISOString().split('T')[0];
}

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

async function fetchComingSoonMovies(): Promise<Movie[]> {
    const response = await fetch(
        'http://localhost:8000/movies/movies/upcoming'
    );
    if (!response.ok) throw new Error('Failed to fetch coming soon movies');
    const data: unknown[] = await response.json();
    // Map TMDB API fields to Movie interface if needed
    const now = new Date();
    const inSixDays = new Date(now);
    inSixDays.setDate(now.getDate() + 6);
    return (
        data as Array<{
            id: number;
            title: string;
            release_date: string;
            poster_path?: string;
        }>
    )
        .map((m) => ({
            id: m.id,
            title: m.title,
            release_date: m.release_date,
            poster_path: 'https://image.tmdb.org/t/p/w500' + m.poster_path,
        }))
        .filter((m) => {
            const release = new Date(m.release_date);
            return release >= now && release <= inSixDays;
        });
}

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
        btn.classList.toggle(
            'active',
            btn instanceof HTMLElement && btn.dataset.value === selectedDay
        );
    });
}

function filterMovies(): Movie[] {
    if (selectedDay === 'coming_soon') {
        const dateLimit = new Date(today);
        dateLimit.setDate(dateLimit.getDate() + 12);
        return movies.filter((m) => new Date(m.release_date) > dateLimit);
    }

    let targetDate: string | null = null;
    if (selectedDay === 'today') targetDate = formatDate(today);
    else if (selectedDay === 'tomorrow') {
        const tmr = new Date(today);
        tmr.setDate(tmr.getDate() + 1);
        targetDate = formatDate(tmr);
    } else {
        targetDate = selectedDay; // is een datum string
    }

    return movies.filter((m) => m.release_date === targetDate);
}

async function renderMovies(): Promise<void> {
    moviesList.innerHTML = '';

    let filtered: Movie[] = [];
    if (selectedDay === 'coming_soon') {
        try {
            filtered = await fetchComingSoonMovies();
        } catch {
            moviesList.innerHTML =
                "<p style='grid-column:1/-1; text-align:center; color:var(--light-grey);'>Failed to load coming soon movies.</p>";
            return;
        }
    } else {
        filtered = filterMovies();
    }

    if (filtered.length === 0) {
        moviesList.innerHTML =
            "<p style='grid-column:1/-1; text-align:center; color:var(--light-grey);'>Geen films gevonden voor deze selectie.</p>";
        return;
    }

    filtered.forEach((movie) => {
        const card = document.createElement('div');
        card.classList.add('movie-card');
        card.innerHTML = `
      <img src="${movie.poster_path}" alt="${movie.title} poster" />
      <h3>${movie.title}</h3>
      <p style="text-align:center; color: var(--light-grey); font-size: 0.9rem;">Release date: ${movie.release_date}</p>
    `;
        moviesList.appendChild(card);
    });
}

// Initialize page
renderFilterButtons();
renderMovies();
