interface Movie {
  id: number;
  title: string;
  poster_path: string;
}

document.addEventListener('DOMContentLoaded', () => {
  // 🔐 Auth-only links zichtbaar maken bij login
  const authOnlyLinks = document.querySelectorAll('.auth-only');
  const isLoggedIn = localStorage.getItem('loggedIn');

  authOnlyLinks.forEach((link) => {
    (link as HTMLElement).style.display = isLoggedIn ? 'inline' : 'none';
  });

  // 🎬 Now Playing movies ophalen
  const grid = document.getElementById('nowPlayingGrid') as HTMLElement;
  if (!grid) return;

  fetch('http://localhost:8000/movies') // Backend endpoint poort en url aanpassen
    .then((response) => {
      if (!response.ok) throw new Error('Network response was not ok');
      return response.json();
    })
    .then((data) => {
      // Controleer of data een array is of object met results property
      let movies: Movie[] = [];

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

        card.appendChild(img);
        card.appendChild(title);

        card.addEventListener('click', () => {
          window.location.href = `movie.html?id=${movie.id}`;
        });

        grid.appendChild(card);
      });
    })
    .catch((error) => {
      console.error('Error loading movies:', error);
    });
});
