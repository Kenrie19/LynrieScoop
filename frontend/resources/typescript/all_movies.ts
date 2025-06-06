import { buildApiUrl } from './config.js';

/**
 * Interface representing detailed information about a movie
 * Contains comprehensive data needed for the movie cards display
 */
interface MovieDetail {
  /** UUID of the movie in the database */
  id: string;
  /** TMDB ID of the movie */
  tmdb_id: number;
  /** Title of the movie */
  title: string;
  /** Plot summary or description */
  overview: string | null;
  /** URL or path to the poster */
  poster_path: string | null;
  /** URL or path to the backdrop (optional) */
  backdrop_path?: string | null;
  /** Release date in ISO format (optional) */
  release_date?: string | null;
  /** Duration in minutes (optional) */
  runtime?: number | null;
  /** Genres as a list of strings (optional) */
  genres?: string[] | null;
  /** Average rating (optional) */
  vote_average?: number | null;
  /** Number of votes (optional) */
  vote_count?: number | null;
  /** Director (optional) */
  director?: string | null;
  /** Cast as a list of strings (optional) */
  cast?: string[] | null;
  /** Trailer URL (optional) */
  trailer_url?: string | null;
  /** Status of the movie (optional) */
  status?: string | null;
}

// Interface for TMDB movie search results which might have different property types
interface TMDBMovie {
  id: number;
  title: string;
  overview: string | null;
  poster_path: string | null;
  backdrop_path?: string | null;
  release_date?: string | null;
  vote_average?: number | null;
  vote_count?: number | null;
}

// DOM Elements
const searchInput = document.getElementById('movie-search') as HTMLInputElement;
const sourceSelect = document.getElementById('movie-source') as HTMLSelectElement;
const moviesGrid = document.getElementById('all-movies-list') as HTMLElement;
const loadingIndicator = document.getElementById('loading-indicator') as HTMLElement;

// Variables to store the movie data
let localMovies: MovieDetail[] = [];
let debounceTimer: number | null = null;

/**
 * Initialize the page when the DOM is fully loaded
 */
document.addEventListener('DOMContentLoaded', async () => {
  console.log('All Movies page initialized');

  // Verify DOM elements
  if (!searchInput) console.error('Search input element not found');
  if (!sourceSelect) console.error('Source select element not found');
  if (!moviesGrid) console.error('Movies grid element not found');
  // Load local movies on page load
  await loadAllMovies();

  // Set up search input event listener with debounce
  searchInput.addEventListener('input', () => {
    if (debounceTimer) {
      window.clearTimeout(debounceTimer);
    }

    debounceTimer = window.setTimeout(() => {
      handleSearch();
    }, 300);
  });

  // Set up source select event listener
  sourceSelect.addEventListener('change', () => {
    handleSearch();
  });
});

/**
 * Fetch all movies from the API
 */
async function loadAllMovies(): Promise<void> {
  showLoading(true);

  try {
    const response = await fetch(buildApiUrl('/movies/movies/'));

    if (!response.ok) {
      throw new Error('Failed to fetch movies');
    }

    const data = await response.json();
    localMovies = Array.isArray(data) ? data : [];

    // Display all movies initially
    displayMovies(localMovies);
  } catch (error) {
    console.error('Error loading movies:', error);
    showError('Failed to load movies. Please try again later.');
  } finally {
    showLoading(false);
  }
}

/**
 * Handle both search input changes and source filter changes
 */
async function handleSearch(): Promise<void> {
  const query = searchInput.value.trim();
  const source = sourceSelect.value;

  showLoading(true);

  try {
    // Filter local movies
    const filteredLocalMovies = localMovies.filter(
      (movie) => !query || movie.title.toLowerCase().includes(query.toLowerCase())
    );

    // Check if we need to include TMDB movies
    if (source === 'all' && query) {
      console.log('Including TMDB movies in search');
      // Only search TMDB if we have a query
      const tmdbResults = await searchTMDBMovies(query);
      console.log(`Received ${tmdbResults.length} TMDB movies`);

      // Filter out TMDB movies that are already in local database
      const localTmdbIds = new Set(localMovies.map((m) => m.tmdb_id));

      // Convert TMDB movies to MovieDetail format
      const formattedTmdbMovies: MovieDetail[] = tmdbResults.map((m) => {
        // Safe access to properties
        const tmdbId =
          typeof m.id === 'number' ? m.id : typeof m.id === 'string' ? parseInt(m.id, 10) : 0;

        return {
          id: tmdbId.toString(),
          tmdb_id: tmdbId,
          title: m.title || 'Unknown Title',
          overview: m.overview || null,
          poster_path: m.poster_path || null,
          backdrop_path: m.backdrop_path || null,
          release_date: m.release_date || null,
          vote_average: typeof m.vote_average === 'number' ? m.vote_average : null,
          vote_count: typeof m.vote_count === 'number' ? m.vote_count : null,
          runtime: null,
          genres: null,
          director: null,
          cast: null,
          trailer_url: null,
          status: null,
        };
      });

      // Filter out duplicates
      const uniqueTmdbMovies = formattedTmdbMovies.filter((m) => !localTmdbIds.has(m.tmdb_id));
      console.log(`After filtering duplicates: ${uniqueTmdbMovies.length} unique TMDB movies`);

      // Combine local and TMDB movies
      displayMovies([...filteredLocalMovies, ...uniqueTmdbMovies]);
    } else {
      displayMovies(filteredLocalMovies);
    }
  } catch (error) {
    console.error('Error handling search:', error);
    showError('An error occurred while searching for movies.');
  } finally {
    showLoading(false);
  }
}

/**
 * Display movies in the grid
 */
function displayMovies(movies: MovieDetail[]): void {
  moviesGrid.innerHTML = '';

  if (movies.length === 0) {
    const noResults = document.createElement('div');
    noResults.className = 'no-results';
    noResults.textContent = 'No movies found matching your search.';
    moviesGrid.appendChild(noResults);
    return;
  }

  movies.forEach((movie) => {
    const card = createMovieCard(movie);
    moviesGrid.appendChild(card);
  });
}

/**
 * Create a movie card element
 */
function createMovieCard(movie: MovieDetail): HTMLElement {
  const card = document.createElement('div');
  card.className = 'movie-card';

  // Is from TMDB indicator
  const isLocalMovie = localMovies.some((m) => m.tmdb_id === movie.tmdb_id);
  if (!isLocalMovie) {
    const tmdbBadge = document.createElement('div');
    tmdbBadge.className = 'tmdb-badge';
    tmdbBadge.textContent = 'TMDB';
    card.appendChild(tmdbBadge);
  }

  // Poster
  const posterBtn = document.createElement('button');
  posterBtn.className = 'poster-btn';
  posterBtn.addEventListener('click', () => {
    window.location.href = `/views/movie_details/index.html?id=${movie.tmdb_id}`;
  });

  const poster = document.createElement('img');
  poster.className = 'movie-poster';

  if (movie.poster_path) {
    poster.src = movie.poster_path.startsWith('http')
      ? movie.poster_path
      : `https://image.tmdb.org/t/p/w500${movie.poster_path}`;
  } else {
    poster.src = '/resources/images/movie_mockup.jpg'; // Fallback image
  }

  poster.alt = `${movie.title} poster`;
  posterBtn.appendChild(poster);

  // Title
  const title = document.createElement('h2');
  title.textContent = movie.title;

  // Rating stars
  const rating = document.createElement('div');
  rating.className = 'movie-rating';
  const stars = Math.round((movie.vote_average || 0) / 2); // Convert from 10-scale to 5-scale

  for (let i = 1; i <= 5; i++) {
    const star = document.createElement('span');
    star.textContent = i <= stars ? '★' : '☆';
    rating.appendChild(star);
  }

  // Overview/description
  const overview = document.createElement('p');
  overview.className = 'movie-overview';
  overview.textContent = movie.overview || 'No description available.';

  // Append elements to card
  card.appendChild(posterBtn);
  card.appendChild(title);
  card.appendChild(rating);
  card.appendChild(overview);

  return card;
}

/**
 * Show or hide loading indicator
 */
function showLoading(isLoading: boolean): void {
  loadingIndicator.style.display = isLoading ? 'flex' : 'none';
}

/**
 * Display error message in the grid
 */
function showError(message: string): void {
  moviesGrid.innerHTML = '';
  const errorEl = document.createElement('div');
  errorEl.className = 'no-results';
  errorEl.textContent = message;
  moviesGrid.appendChild(errorEl);
}

/**
 * Search for movies in TMDB
 */
async function searchTMDBMovies(query: string): Promise<TMDBMovie[]> {
  if (!query) return [];

  try {
    console.log(`Searching TMDB for: ${query}`);
    // Make sure we're using the correct API endpoint path
    const apiUrl = buildApiUrl(`/movies/movies/search?query=${encodeURIComponent(query)}`);
    console.log(`API URL: ${apiUrl}`);

    const response = await fetch(apiUrl);
    console.log(`TMDB search status: ${response.status}`);

    if (!response.ok) {
      if (response.status === 404) {
        console.log('No TMDB results found');
        return []; // No results is okay
      }

      // Try to get error details
      try {
        const errorData = await response.text();
        console.error('TMDB search error response:', errorData);
      } catch {
        console.error('Could not read error response body');
      }

      throw new Error(`Failed to search TMDB movies: ${response.statusText}`);
    }

    const data = await response.json();
    console.log(`TMDB results:`, data);
    const results = Array.isArray(data) ? data : data.results || [];
    console.log(`Formatted ${results.length} TMDB results`);
    return results;
  } catch (error) {
    console.error('Error searching TMDB movies:', error);
    return [];
  }
}
