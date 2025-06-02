import { buildApiUrl } from './config.js';
import { getCookie, decodeJwtPayload } from './cookies.js';

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
  const addMovieFeedback = document.getElementById('addMovieFeedback')!;
  const allMoviesList = document.getElementById('allMoviesList')!;

  searchTmdbInput.addEventListener('input', async () => {
    const query = searchTmdbInput.value.trim();
    tmdbSearchResults.replaceChildren();
    addMovieFeedback.textContent = '';
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
        img.src = movie.poster_path ? `https://image.tmdb.org/t/p/w200${movie.poster_path}` : '';
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

        importBtn.addEventListener('click', () => importMovieByTmdbId(movie.id));

        titleBtnWrapper.appendChild(title);
        titleBtnWrapper.appendChild(importBtn);

        container.appendChild(img);
        container.appendChild(titleBtnWrapper);

        tmdbSearchResults.appendChild(container);
      });
    } catch {
      tmdbSearchResults.textContent = 'Error fetching search results.';
    }
  });

  async function importMovieByTmdbId(tmdbId: string) {
    addMovieFeedback.textContent = '';
    try {
      const res = await fetch(buildApiUrl(`/admin/admin/tmdb/import/${tmdbId}`), {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (res.ok) {
        addMovieFeedback.textContent = '✅ Movie successfully imported!';
        await loadAllMovies();
      } else {
        const errData = await res.json();
        addMovieFeedback.textContent = errData.detail || 'Failed to import movie.';
      }
    } catch {
      addMovieFeedback.textContent = 'Network error. Please try again.';
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
        img.src = movie.poster_path ? `https://image.tmdb.org/t/p/w200${movie.poster_path}` : '';
        img.alt = movie.title;

        const titleBtnWrapper = document.createElement('div');
        titleBtnWrapper.style.display = 'flex';
        titleBtnWrapper.style.flexDirection = 'column';
        titleBtnWrapper.style.alignItems = 'center';
        titleBtnWrapper.style.width = '100%';

        const title = document.createElement('span');
        title.textContent = movie.title;
        title.style.textAlign = 'center';

        titleBtnWrapper.appendChild(title);

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
