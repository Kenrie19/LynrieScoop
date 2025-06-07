import { buildApiUrl } from './config.js';
import { getCookie, decodeJwtPayload } from './cookies.js';

const FALLBACK_POSTER = '/resources/images/movie_mockup.jpg';

type Movie = {
  id: string;
  title: string;
  poster_path?: string | null;
};

document.addEventListener('DOMContentLoaded', () => {
  const token = getCookie('token');
  if (!token) {
    window.location.href = '/views/login';
    return;
  }
  const user = decodeJwtPayload(token);
  if (!user || user.role !== 'manager') {
    alert('Access denied. Admins only.');
    window.location.href = '/views/login';
    return;
  }

  const searchTmdbInput = document.getElementById('searchTmdb') as HTMLInputElement;
  const tmdbSearchResults = document.getElementById('tmdbSearchResults')!;
  const allMoviesList = document.getElementById('allMoviesList')!;

  searchTmdbInput.addEventListener('input', async () => {
    const query = searchTmdbInput.value.trim();
    tmdbSearchResults.replaceChildren();
    if (query.length < 2) return;

    try {
      const res = await fetch(
        buildApiUrl(`/movies/movies/search?query=${encodeURIComponent(query)}`),
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );
      const data: Movie[] = await res.json();

      if (!Array.isArray(data) || data.length === 0) {
        tmdbSearchResults.textContent = 'No results found.';
        return;
      }

      data.forEach((movie) => {
        const container = document.createElement('div');
        container.className = 'movie-result';

        const img = document.createElement('img');
        img.src = movie.poster_path
          ? `https://image.tmdb.org/t/p/w200${movie.poster_path}`
          : FALLBACK_POSTER;
        img.alt = movie.title;

        const titleBtnWrapper = document.createElement('div');
        titleBtnWrapper.style.display = 'flex';
        titleBtnWrapper.style.flexDirection = 'column';
        titleBtnWrapper.style.alignItems = 'center';
        titleBtnWrapper.style.width = '100%';

        const title = document.createElement('span');
        title.textContent = movie.title;
        title.style.marginBottom = '0.5rem';
        title.style.textAlign = 'center';

        const importBtn = document.createElement('button');
        importBtn.className = 'btn';
        importBtn.textContent = 'Import';
        importBtn.addEventListener('click', () => importMovieByTmdbId(movie.id, container));

        const feedback = document.createElement('div');
        feedback.className = 'feedback';

        titleBtnWrapper.appendChild(title);
        titleBtnWrapper.appendChild(importBtn);
        titleBtnWrapper.appendChild(feedback);

        container.appendChild(img);
        container.appendChild(titleBtnWrapper);
        tmdbSearchResults.appendChild(container);
      });
    } catch {
      tmdbSearchResults.textContent = 'Error fetching search results.';
    }
  });

  async function importMovieByTmdbId(tmdbId: string, container: HTMLElement) {
    const feedback = container.querySelector('.feedback') as HTMLElement;
    feedback.textContent = '';

    try {
      const res = await fetch(buildApiUrl(`/admin/admin/tmdb/import/${tmdbId}`), {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (res.ok) {
        feedback.textContent = 'Movie successfully imported!';
        feedback.classList.remove('error');
        feedback.classList.add('success');
        await loadAllMovies();
      } else {
        const errData = await res.json();
        feedback.textContent = errData.detail || 'Failed to import movie.';
        feedback.classList.add('error');
      }
    } catch {
      feedback.textContent = 'Network error. Please try again.';
      feedback.classList.add('error');
    }
  }

  async function loadAllMovies() {
    allMoviesList.replaceChildren();

    try {
      const res = await fetch(buildApiUrl('/movies/movies/'), {
        headers: { Authorization: `Bearer ${token}` },
      });
      const movies: Movie[] = await res.json();

      if (!Array.isArray(movies)) {
        allMoviesList.textContent = 'Failed to load movies.';
        return;
      }

      movies.forEach((movie) => {
        const container = document.createElement('div');
        container.className = 'movie-result';

        const img = document.createElement('img');
        img.src = movie.poster_path
          ? `https://image.tmdb.org/t/p/w200${movie.poster_path}`
          : FALLBACK_POSTER;
        img.alt = movie.title;

        const titleBtnWrapper = document.createElement('div');
        titleBtnWrapper.style.display = 'flex';
        titleBtnWrapper.style.flexDirection = 'column';
        titleBtnWrapper.style.alignItems = 'center';
        titleBtnWrapper.style.width = '100%';

        const title = document.createElement('span');
        title.textContent = movie.title;
        title.style.textAlign = 'center';

        const deleteBtn = document.createElement('button');
        deleteBtn.className = 'btn btn-delete';
        deleteBtn.textContent = 'Delete';

        deleteBtn.addEventListener('click', async () => {
          const confirmed = confirm(`Are you sure you want to delete "${movie.title}"?`);
          if (!confirmed) return;

          try {
            const res = await fetch(buildApiUrl(`/admin/admin/movies/${movie.id}`), {
              method: 'DELETE',
              headers: {
                Authorization: `Bearer ${token}`,
              },
            });

            if (res.ok) {
              await loadAllMovies();
            } else {
              alert('Failed to delete movie');
            }
          } catch {
            alert('Network error while deleting movie');
          }
        });

        titleBtnWrapper.appendChild(title);
        titleBtnWrapper.appendChild(deleteBtn);

        container.appendChild(img);
        container.appendChild(titleBtnWrapper);
        allMoviesList.appendChild(container);
      });
    } catch {
      allMoviesList.textContent = 'Error loading movies.';
    }
  }

  loadAllMovies();
});
