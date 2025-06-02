import { buildApiUrl } from './config.js';

/**
 * Represents detailed information about a movie.
 * Contains comprehensive data needed for the movie detail page.
 * @interface
 */

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

document.addEventListener('DOMContentLoaded', () => {
  /**
   * Retrieves and displays the popular movies
   */
  // Trending movies ophalen
  const grid = document.getElementById('trendingMoviesGrid') as HTMLElement;
  if (!grid) return; /**
   * Fetches popular movies from the API
   */
  fetch(buildApiUrl('/movies/movies/popular'))
    .then((response) => {
      if (!response.ok) throw new Error('Network response was not ok');
      return response.json();
    })
    .then((data) => {
      // Controleer of data een array is of object met results property
      let movies: MovieDetail[] = [];

      if (Array.isArray(data)) {
        movies = data; // backend geeft direct een array terug
      } else if (Array.isArray(data.results)) {
        movies = data.results; // backend geeft object met results array
      } else {
        console.error('Unexpected movies data format:', data);
        return;
      }

      movies.forEach((movie) => {
        const card = document.createElement('div');
        card.classList.add('movie-card');

        const img = document.createElement('img');
        img.src =
          movie.poster_path && movie.poster_path.startsWith('http')
            ? movie.poster_path
            : movie.poster_path
              ? `https://image.tmdb.org/t/p/w500${movie.poster_path}`
              : 'path/to/default/poster.jpg'; // Provide a default image path if poster_path is undefined
        img.alt = movie.title;

        const title = document.createElement('h3');
        title.textContent = movie.title;

        // Sterren (vote_average)
        const rating = document.createElement('div');
        rating.className = 'movie-rating';
        const stars = Math.round((movie.vote_average || 0) / 2); // 0-10 schaal naar 0-5 sterren
        for (let i = 1; i <= 5; i++) {
          const star = document.createElement('span');
          star.textContent = i <= stars ? '★' : '☆';
          rating.appendChild(star);
        }

        card.appendChild(img);
        card.appendChild(title);
        card.appendChild(rating);

        card.addEventListener('click', () => {
          window.location.href = `views/movie_details/index.html?id=${movie.id}`; // Link naar movie details pagina (output static site)
        });

        grid.appendChild(card);
      });
    })
    .catch((error) => {
      console.error('Error loading movies:', error);
    });
});

const nowPlayingGrid = document.getElementById('nowPlayingMoviesGrid') as HTMLElement;
if (nowPlayingGrid) {
  fetch(buildApiUrl('/showings/showings/now-playing'))
    .then((response) => {
      if (!response.ok) throw new Error('Failed to fetch now playing movies');
      return response.json();
    })
    .then((movies: MovieDetail[]) => {
      movies.forEach((movie) => {
        const card = document.createElement('div');
        card.classList.add('movie-card');

        const img = document.createElement('img');
        img.src = movie.poster_path
          ? movie.poster_path.startsWith('http')
            ? movie.poster_path
            : `https://image.tmdb.org/t/p/w500${movie.poster_path}`
          : 'path/to/default/poster.jpg';
        img.alt = movie.title;

        const title = document.createElement('h3');
        title.textContent = movie.title;

        const rating = document.createElement('div');
        rating.className = 'movie-rating';
        const stars = Math.round((movie.vote_average || 0) / 2);
        for (let i = 1; i <= 5; i++) {
          const star = document.createElement('span');
          star.textContent = i <= stars ? '★' : '☆';
          rating.appendChild(star);
        }

        card.appendChild(img);
        card.appendChild(title);
        card.appendChild(rating);

        card.addEventListener('click', () => {
          window.location.href = `views/movie_details/index.html?id=${movie.tmdb_id}`;
        });

        nowPlayingGrid.appendChild(card);
      });
    })
    .catch(() => {});
}
