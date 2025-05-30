import { getCookie, decodeJwtPayload } from './cookies.js';

document.addEventListener('DOMContentLoaded', () => {
  const token = getCookie('token');
  if (!token) return redirectToLogin();

  const user = decodeJwtPayload(token);
  if (!user || user.role !== 'admin') {
    alert('Access denied. Admins only.');
    return redirectToLogin();
  }

  const searchInput = document.getElementById('search') as HTMLInputElement;
  const resultsContainer = document.getElementById('searchResults')!;
  const screeningForm = document.getElementById('screeningForm')!;
  const selectedTitleSpan = document.getElementById('selectedTitle')!;
  const feedback = document.getElementById('feedbackMessage')!;
  const screeningsList = document.getElementById('screeningsList')!;

  let selectedMovieId: number | null = null;

  searchInput.addEventListener('input', async () => {
    const query = searchInput.value.trim();
    resultsContainer.replaceChildren();
    if (query.length < 2) return;

    const res = await fetch(
      `http://localhost:8000/movies/movies/search?query=${encodeURIComponent(query)}`,
      {
        headers: { Authorization: `Bearer ${token}` },
      }
    );

    const data = await res.json();
    if (!Array.isArray(data)) return;

    data.forEach((movie) => {
      const container = document.createElement('div');
      container.className = 'movie-result';

      const img = document.createElement('img');
      img.src = `https://image.tmdb.org/t/p/w200${movie.poster_path}`;
      img.alt = movie.title;

      const title = document.createElement('span');
      title.textContent = movie.title;

      container.appendChild(img);
      container.appendChild(title);
      container.addEventListener('click', () => {
        selectedMovieId = movie.tmdb_id ?? movie.id;
        selectedTitleSpan.textContent = movie.title;
        screeningForm.style.display = 'block';
        feedback.textContent = '';
      });

      resultsContainer.appendChild(container);
    });
  });

  const addBtn = document.getElementById('addScreening')!;
  addBtn.addEventListener('click', async () => {
    if (!selectedMovieId) return;

    const date = (document.getElementById('date') as HTMLInputElement).value;
    const time = (document.getElementById('time') as HTMLInputElement).value;
    const room = (document.getElementById('room') as HTMLSelectElement).value;
    const datetime = `${date}T${time}:00`;

    const response = await fetch('http://localhost:8000/screenings/screenings/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        movie_id: selectedMovieId,
        room_id: room,
        start_time: datetime,
        end_time: datetime,
        price: 10,
      }),
    });

    if (response.ok) {
      feedback.textContent = '✅ Screening successfully added!';
      screeningForm.style.display = 'none';
      await loadScreenings();
    } else {
      feedback.textContent = '❌ Failed to add screening.';
    }
  });

  type Screening = {
    // Possibly incomplete type
    id: number;
    movie_title?: string;
    movie_id: number;
    room_id: number | string;
    start_time: string;
    end_time: string;
    price: number;
  };

  async function loadScreenings() {
    screeningsList.replaceChildren();
    const res = await fetch('http://localhost:8000/screenings/screenings/');
    const data: Screening[] = await res.json();

    const upcomingScreenings = data
      .filter((s: Screening) => new Date(s.start_time) >= new Date())
      .sort(
        (a: Screening, b: Screening) =>
          new Date(a.start_time).getTime() - new Date(b.start_time).getTime()
      );

    const grouped: Record<string, Screening[]> = {};
    upcomingScreenings.forEach((s: Screening) => {
      const date = new Date(s.start_time).toLocaleDateString('en-GB', {
        weekday: 'long',
        day: 'numeric',
        month: 'long',
      });
      if (!grouped[date]) grouped[date] = [];
      grouped[date].push(s);
    });

    Object.keys(grouped).forEach((day) => {
      const screenings = grouped[day];
      const title = document.createElement('h3');
      title.textContent = day;
      screeningsList.appendChild(title);

      screenings.forEach((screening: Screening) => {
        const card = document.createElement('div');
        card.className = 'screening-card';

        const info = document.createElement('div');
        info.className = 'screening-info';

        const movieTitle = document.createElement('strong');
        movieTitle.textContent = screening.movie_title ?? 'Unknown movie';

        const time = document.createElement('p');
        time.textContent = new Date(screening.start_time).toLocaleTimeString([], {
          hour: '2-digit',
          minute: '2-digit',
        });

        const room = document.createElement('p');
        room.textContent = `Room ${screening.room_id}`;

        info.appendChild(movieTitle);
        info.appendChild(time);
        info.appendChild(room);

        const actions = document.createElement('div');
        actions.className = 'screening-actions';

        const editBtn = document.createElement('button');
        editBtn.className = 'edit';
        editBtn.textContent = 'Edit';
        editBtn.addEventListener('click', () => {
          const currentDate = new Date(screening.start_time);
          const newDate = prompt('New date (YYYY-MM-DD):', currentDate.toISOString().split('T')[0]);
          if (!newDate) return;
          const newTime = prompt('New time (HH:MM):', currentDate.toTimeString().slice(0, 5));
          if (!newTime) return;
          const newRoom = prompt('New room:', String(screening.room_id));
          if (!newRoom) return;

          const newDatetime = `${newDate}T${newTime}:00`;

          fetch(`http://localhost:8000/screenings/screenings/${screening.id}`, {
            method: 'PUT',
            headers: {
              Authorization: `Bearer ${token}`,
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              room_id: newRoom,
              start_time: newDatetime,
              end_time: newDatetime,
              price: screening.price,
            }),
          }).then((res) => {
            if (res.ok) loadScreenings();
            else alert('Failed to update screening.');
          });
        });

        const deleteBtn = document.createElement('button');
        deleteBtn.className = 'delete';
        deleteBtn.textContent = 'Delete';
        deleteBtn.addEventListener('click', async () => {
          const confirmed = confirm('Are you sure you want to delete this screening?');
          if (!confirmed) return;

          const delRes = await fetch(
            `http://localhost:8000/screenings/screenings/${screening.id}`,
            {
              method: 'DELETE',
              headers: { Authorization: `Bearer ${token}` },
            }
          );

          if (delRes.ok) loadScreenings();
          else alert('Failed to delete screening.');
        });

        actions.append(editBtn, deleteBtn);
        card.append(info, actions);
        screeningsList.appendChild(card);
      });
    });
  }

  function redirectToLogin() {
    window.location.href = '/views/login';
  }

  loadScreenings();
});
