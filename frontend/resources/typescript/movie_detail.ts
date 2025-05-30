/**
 * Represents detailed information about a movie.
 * Contains comprehensive data needed for the movie detail page.
 * @interface
 */

interface Genre {
  /** Unique identifier for the genre */
  id: number;
  /** Name of the genre */
  name: string;
}

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
      // Render movie details zonder inline styling
      container.innerHTML = `
        <div class="movie-detail-card">
          <img class="movie-detail-poster" src="https://image.tmdb.org/t/p/w500${movie.poster_path}" alt="${movie.title}">
          <div class="movie-detail-info">
            <h1>${movie.title}</h1>
            <p><strong>Release date:</strong> ${movie.release_date || 'N/A'}</p>
            <p><strong>Runtime:</strong> ${movie.runtime ? movie.runtime + ' min' : 'N/A'}</p>
            <p><strong>Status:</strong> ${movie.status || 'N/A'}</p>
            <p><strong>Genres:</strong> ${
              movie.genres && movie.genres.length > 0
                ? movie.genres
                    .map((genre: string | Genre) =>
                      typeof genre === 'string' ? genre : genre.name
                    )
                    .join(', ')
                : 'N/A'
            }</p>
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
