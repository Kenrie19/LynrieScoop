interface Genre {
  id: number;
  name: string;
}

interface MovieDetail {
  id: number;
  title: string;
  overview: string;
  poster_path: string;
  backdrop_path?: string;
  release_date?: string;
  runtime?: number;
  genres?: Genre[];
  vote_average?: number;
  vote_count?: number;
  director?: string | null;
  cast?: string | null;
  trailer_url?: string | null;
  status?: string;
}

document.addEventListener('DOMContentLoaded', () => {
  const params = new URLSearchParams(window.location.search);
  const movieId = params.get('id');
  const container = document.getElementById('movieDetailContainer');
  if (!movieId || !container) return;

  fetch(`http://localhost:8000/movies/movies/tmdb/${movieId}`)
    .then(response => {
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
            <p><strong>Genres:</strong> ${(movie.genres && movie.genres.length > 0) ? movie.genres.map(g => g.name).join(', ') : 'N/A'}</p>
            <p><strong>Rating:</strong> ${movie.vote_average ? movie.vote_average.toFixed(1) : 'N/A'} (${movie.vote_count || 0} votes)</p>
            <p><strong>Overview:</strong> ${movie.overview}</p>
          </div>
        </div>
      `;
    })
    .catch(error => {
      container.innerHTML = '<p>Error loading movie details.</p>';
      console.error('Error loading movie details:', error);
    });
});
