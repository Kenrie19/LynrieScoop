import { getCookie, decodeJwtPayload } from './cookies.js';

document.addEventListener('DOMContentLoaded', () => {
  const token = getCookie('token');
  if (!token) return redirectToLogin();

  const user = decodeJwtPayload(token);
  if (!user || user.role !== 'manager') {
    alert('Access denied. Admins only.');
    return redirectToLogin();
  }

  const searchInput = document.getElementById('search') as HTMLInputElement;
  const resultsContainer = document.getElementById('searchResults')!;
  const screeningForm = document.getElementById('screeningForm')!;
  const selectedTitleSpan = document.getElementById('selectedTitle')!;
  const feedback = document.getElementById('feedbackMessage')!;
  const screeningsList = document.getElementById('screeningsList')!;

  let selectedMovieId: string | null = null;

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
    if (!Array.isArray(data)) {
      feedback.textContent = '❌ Invalid search response.';
      return;
    }

    data.forEach((movie) => {
      const container = document.createElement('div');
      container.className = 'movie-result';

      const img = document.createElement('img');
      img.src = movie.poster_path ? `https://image.tmdb.org/t/p/w200${movie.poster_path}` : '';
      img.alt = movie.title;

      const title = document.createElement('span');
      title.textContent = movie.title;

      container.appendChild(img);
      container.appendChild(title);
      container.addEventListener('click', () => {
        selectedMovieId = movie.id;
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

    const response = await fetch('http://localhost:8000/showings/showings/', {
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
    id: string;
    movie_id: string;
    room_id: string;
    start_time: string;
    end_time: string;
    price: number;
  };

  async function loadScreenings() {
    screeningsList.replaceChildren();

    try {
      const movieRes = await fetch('http://localhost:8000/movies/movies/', {
        headers: { Authorization: `Bearer ${token}` },
      });
      const movies = await movieRes.json();
      const movieMap = new Map<string, { title: string; poster_path?: string }>();
      if (Array.isArray(movies)) {
        movies.forEach((movie) => {
          movieMap.set(movie.id, { title: movie.title, poster_path: movie.poster_path });
        });
      }

      const cinemasRes = await fetch('http://localhost:8000/admin/admin/cinemas', {
        headers: { Authorization: `Bearer ${token}` },
      });
      const cinemas = await cinemasRes.json();
      if (!Array.isArray(cinemas) || cinemas.length === 0) {
        feedback.textContent = '❌ No cinemas found.';
        return;
      }
      const cinemaId = cinemas[0].id;

      const roomsRes = await fetch(`http://localhost:8000/admin/admin/cinemas/${cinemaId}/rooms`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      const rooms = await roomsRes.json();
      const roomMap = new Map<string, string>();
      if (Array.isArray(rooms)) {
        rooms.forEach((room) => {
          roomMap.set(room.id, room.name || 'Unknown room');
        });
      }

      const res = await fetch('http://localhost:8000/admin/admin/showings', {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      const data = await res.json();
      if (!Array.isArray(data)) {
        feedback.textContent = '❌ Unexpected response from server.';
        console.error('Screening data not array:', data);
        return;
      }

      const upcomingScreenings = data
        .filter((s: Screening) => new Date(s.start_time) >= new Date())
        .sort((a, b) => new Date(a.start_time).getTime() - new Date(b.start_time).getTime());

      const grouped: Record<string, Screening[]> = {};
      upcomingScreenings.forEach((s) => {
        const date = new Date(s.start_time).toLocaleDateString('en-GB', {
          weekday: 'long',
          day: 'numeric',
          month: 'long',
        });
        if (!grouped[date]) grouped[date] = [];
        grouped[date].push(s);
      });

      Object.entries(grouped).forEach(([day, screenings]) => {
        const dayTitle = document.createElement('h3');
        dayTitle.textContent = day;
        screeningsList.appendChild(dayTitle);

        screenings.forEach((screening) => {
          const card = document.createElement('div');
          card.className = 'screening-card';
          card.style.display = 'flex';
          card.style.alignItems = 'flex-start';
          card.style.gap = '1rem';
          card.style.flexWrap = 'wrap';

          // Poster img left
          const movie = movieMap.get(screening.movie_id);
          if (movie && movie.poster_path) {
            const img = document.createElement('img');
            img.src = `https://image.tmdb.org/t/p/w92${movie.poster_path}`;
            img.alt = movie.title;
            img.style.width = '60px';
            img.style.height = 'auto';
            img.style.flexShrink = '0';
            card.appendChild(img);
          }

          // Info + edit container vertical stack
          const rightContainer = document.createElement('div');
          rightContainer.style.flexGrow = '1';
          rightContainer.style.minWidth = '250px';

          // Info block
          const info = document.createElement('div');
          info.className = 'screening-info';

          const movieTitle = document.createElement('strong');
          movieTitle.textContent = movie?.title ?? 'Unknown movie';

          const time = document.createElement('p');
          time.textContent = new Date(screening.start_time).toLocaleTimeString([], {
            hour: '2-digit',
            minute: '2-digit',
          });

          const room = document.createElement('p');
          room.textContent = `${roomMap.get(screening.room_id) ?? screening.room_id}`;

          info.appendChild(movieTitle);
          info.appendChild(time);
          info.appendChild(room);
          rightContainer.appendChild(info);

          // Inline edit container styled like add form
          const editContainer = document.createElement('div');
          editContainer.style.marginTop = '1rem';
          editContainer.style.display = 'none';
          editContainer.className = 'form-section'; // Use your add form styles

          // Date label + input
          const dateLabel = document.createElement('label');
          dateLabel.textContent = 'Date:';
          const dateInput = document.createElement('input');
          dateInput.type = 'date';
          dateInput.value = new Date(screening.start_time).toISOString().split('T')[0];
          dateInput.style.marginTop = '0.25rem';
          dateInput.style.width = '100%';

          // Time label + input
          const timeLabel = document.createElement('label');
          timeLabel.textContent = 'Time:';
          const timeInput = document.createElement('input');
          timeInput.type = 'time';
          timeInput.value = new Date(screening.start_time).toTimeString().slice(0, 5);
          timeInput.style.marginTop = '0.25rem';
          timeInput.style.width = '100%';

          // Room label + select
          const roomLabel = document.createElement('label');
          roomLabel.textContent = 'Room:';
          const roomInput = document.createElement('select');
          roomInput.style.marginTop = '0.25rem';
          roomInput.style.width = '100%';
          roomMap.forEach((name, id) => {
            const option = document.createElement('option');
            option.value = id;
            option.textContent = name;
            if (id === screening.room_id) option.selected = true;
            roomInput.appendChild(option);
          });

          // Buttons container
          const btnContainer = document.createElement('div');
          btnContainer.style.marginTop = '1rem';
          btnContainer.style.display = 'flex';
          btnContainer.style.gap = '0.5rem';

          // Save button
          const saveBtn = document.createElement('button');
          saveBtn.textContent = 'Save';
          saveBtn.style.flexGrow = '1';
          saveBtn.addEventListener('click', () => {
            const newDate = dateInput.value;
            const newTime = timeInput.value;
            const newRoom = roomInput.value;
            if (!newDate || !newTime || !newRoom) {
              alert('Please fill all fields');
              return;
            }
            const newDatetime = `${newDate}T${newTime}:00`;

            fetch(`http://localhost:8000/showings/showings/${screening.id}`, {
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
              if (res.ok) {
                loadScreenings();
              } else {
                alert('Failed to update screening.');
              }
            });
          });

          // Cancel button
          const cancelBtn = document.createElement('button');
          cancelBtn.textContent = 'Cancel';
          cancelBtn.style.flexGrow = '1';
          cancelBtn.addEventListener('click', () => {
            editContainer.style.display = 'none';
          });

          btnContainer.appendChild(saveBtn);
          btnContainer.appendChild(cancelBtn);

          // Append all to editContainer
          editContainer.appendChild(dateLabel);
          editContainer.appendChild(dateInput);
          editContainer.appendChild(timeLabel);
          editContainer.appendChild(timeInput);
          editContainer.appendChild(roomLabel);
          editContainer.appendChild(roomInput);
          editContainer.appendChild(btnContainer);

          // Edit and Delete buttons
          const actions = document.createElement('div');
          actions.className = 'screening-actions';
          actions.style.display = 'flex';
          actions.style.alignItems = 'center';
          actions.style.marginTop = '0.5rem';

          const editBtn = document.createElement('button');
          editBtn.className = 'edit';
          editBtn.textContent = 'Edit';
          editBtn.style.marginRight = '0.5rem';
          editBtn.addEventListener('click', () => {
            editContainer.style.display = editContainer.style.display === 'none' ? 'block' : 'none';
          });

          const deleteBtn = document.createElement('button');
          deleteBtn.className = 'delete';
          deleteBtn.textContent = 'Delete';
          deleteBtn.addEventListener('click', async () => {
            if (!confirm('Are you sure you want to delete this screening?')) return;

            const delRes = await fetch(`http://localhost:8000/showings/showings/${screening.id}`, {
              method: 'DELETE',
              headers: { Authorization: `Bearer ${token}` },
            });

            if (delRes.ok) loadScreenings();
            else alert('Failed to delete screening.');
          });

          actions.append(editBtn, deleteBtn);

          rightContainer.appendChild(actions);
          rightContainer.appendChild(editContainer);

          card.appendChild(rightContainer);

          screeningsList.appendChild(card);
        });
      });
    } catch (err) {
      console.error('Error loading screenings:', err);
      feedback.textContent = '❌ Failed to load screenings.';
    }
  }

  function redirectToLogin() {
    window.location.href = '/views/login';
  }

  loadScreenings();
});
