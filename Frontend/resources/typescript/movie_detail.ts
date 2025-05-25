/**
 * Represents a movie genre with its identifier and name.
 * @interface
 */
interface Genre {
  /** Unique identifier for the genre */
  id: number;
  /** Name of the genre */
  name: string;
}

/**
 * Represents detailed information about a movie.
 * Contains comprehensive data needed for the movie detail page.
 * @interface
 */
interface MovieDetail {
  /** Unique identifier for the movie */
  id: number;
  /** Title of the movie */
  title: string;
  /** Plot summary or description of the movie */
  overview: string;
  /** URL or path to the movie poster image */
  poster_path: string;
  /** URL or path to the movie backdrop image (optional) */
  backdrop_path?: string;
  /** Release date of the movie in ISO format (YYYY-MM-DD) (optional) */
  release_date?: string;
  /** Duration of the movie in minutes (optional) */
  runtime?: number;
  /** List of genres the movie belongs to (optional) */
  genres?: Genre[];
  /** Average rating of the movie on a scale of 0-10 (optional) */
  vote_average?: number;
  /** Number of votes received for the rating (optional) */
  vote_count?: number;
  /** Name of the movie director (optional) */
  director?: string | null;
  /** List of cast members (optional) */
  cast?: string | null;
  /** URL to the movie trailer (optional) */
  trailer_url?: string | null;
  /** Current status of the movie (e.g., "Released", "In Production") (optional) */
  status?: string;
}

/**
 * Initializes the movie detail page when the DOM is fully loaded.
 * Retrieves movie details from the API based on the movie ID in the URL parameters.
 */
document.addEventListener('DOMContentLoaded', () => {
  const params = new URLSearchParams(window.location.search);
  const movieId = params.get('id');
  const container = document.getElementById('movieDetailContainer');
  if (!movieId || !container) return;

  fetch(`http://localhost:8000/movies/movies/tmdb/${movieId}`)
    .then((response) => {
      if (!response.ok) throw new Error('Network response was not ok');
      return response.json();
    })
    .then((movie: MovieDetail) => {
      // Log de movie data om te zien wat er terugkomt
      console.log('Movie detail data:', movie);
      // Render movie details
      container.innerHTML = `
        <div class="movie-detail-card">
          <img class="movie-detail-poster" src="https://image.tmdb.org/t/p/w500${movie.poster_path}" alt="${movie.title}">
          <div class="movie-detail-info">
            <h1>${movie.title}</h1>
            <p><strong>Release date:</strong> ${movie.release_date || 'N/A'}</p>
            <p><strong>Runtime:</strong> ${movie.runtime ? movie.runtime + ' min' : 'N/A'}</p>
            <p><strong>Status:</strong> ${movie.status || 'N/A'}</p>
            <p><strong>Genres:</strong> ${movie.genres && movie.genres.length > 0 ? movie.genres.map((g) => g.name).join(', ') : 'N/A'}</p>
            <p><strong>Rating:</strong> ${movie.vote_average ? movie.vote_average.toFixed(1) : 'N/A'} (${movie.vote_count || 0} votes)</p>
            <p><strong>Overview:</strong> ${movie.overview}</p>
          </div>
        </div>
      `;
    })
    .catch((error) => {
      container.innerHTML = '<p>Error loading movie details.</p>';
      console.error('Error loading movie details:', error);
    });
});
