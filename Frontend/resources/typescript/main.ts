interface Movie {
  id: number;
  title: string;
  poster_path: string;
}

document.addEventListener('DOMContentLoaded', () => {
  // 🔐 Auth-only links zichtbaar maken bij login
  const authOnlyLinks = document.querySelectorAll('.auth-only');
  const isLoggedIn = localStorage.getItem('loggedIn');

  authOnlyLinks.forEach(link => {
    (link as HTMLElement).style.display = isLoggedIn ? 'inline' : 'none';
  });

  // 🎬 Now Playing movies ophalen
  const grid = document.getElementById('nowPlayingGrid') as HTMLElement;

  fetch('http://localhost:3000/movies') // Vervang met jouw backend endpoint
    .then(response => {
      if (!response.ok) throw new Error('Network response was not ok');
      return response.json();
    })
    .then(data => {
      const movies: Movie[] = data.results;
      movies.forEach(movie => {
        const card = document.createElement('div');
        card.classList.add('movie-card');

        const img = document.createElement('img');
        img.src = `https://image.tmdb.org/t/p/w500${movie.poster_path}`;
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
    .catch(error => {
      console.error('Error loading movies:', error);
    });
});
