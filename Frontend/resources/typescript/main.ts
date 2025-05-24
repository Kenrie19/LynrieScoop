/**
 * Represents a movie with its basic information.
 * @interface
 */
interface Movie {
  /** Unique identifier for the movie */
  id: number;
  /** Title of the movie */
  title: string;
  /** URL or path to the movie poster image */
  poster_path: string;
  /** Plot summary of the movie (optional) */
  overview?: string;
  /** Average rating of the movie on a scale of 0-10 (optional) */
  vote_average?: number;
}

/**
 * Initializes the page content when the DOM is fully loaded.
 * Handles authentication-dependent UI elements and fetches now playing movies.
 */
document.addEventListener('DOMContentLoaded', () => {
  // 🔐 Auth-only links zichtbaar maken bij login
  const authOnlyLinks = document.querySelectorAll('.auth-only');
  const isLoggedIn = localStorage.getItem('loggedIn');

  /**
   * Shows or hides authentication-dependent elements based on login status
   */
  authOnlyLinks.forEach((link) => {
    (link as HTMLElement).style.display = isLoggedIn ? 'inline' : 'none';
  });
  /**
   * Retrieves and displays the currently playing movies
   */
  // 🎬 Now Playing movies ophalen
  const grid = document.getElementById('nowPlayingGrid') as HTMLElement;
  if (!grid) return;

  /**
   * Fetches now playing movies from the API
   */
  fetch('http://localhost:8000/movies/movies/now_playing') // Backend endpoint poort en url aanpassen
    .then((response) => {
      if (!response.ok) throw new Error('Network response was not ok');
      return response.json();
    })
    .then((data) => {
      // Controleer of data een array is of object met results property
      let movies: Movie[] = [];
      // Log de data om te zien wat er terugkomt
      console.log('Movies data:', data);

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
        img.src = movie.poster_path.startsWith('http')
          ? movie.poster_path
          : `https://image.tmdb.org/t/p/w500${movie.poster_path}`;
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
