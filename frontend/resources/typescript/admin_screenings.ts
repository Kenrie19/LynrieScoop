import { getCookie, decodeJwtPayload } from './cookies.js';
import { buildApiUrl } from './config.js';

interface Room {
  id: string;
  name?: string;
}

interface Movie {
  id: string;
  tmdb_id: number;
  title: string;
  poster_path?: string;
  runtime?: number;
}

interface Screening {
  id: string;
  movie_id: string; // local UUID for showings
  room_id: string;
  start_time: string;
  end_time: string;
  price: number;
}

document.addEventListener('DOMContentLoaded', () => {
  const token = getCookie('token');
  if (!token) return redirectToLogin();

  const user = decodeJwtPayload(token);
  if (!user || user.role !== 'manager') {
    alert('Access denied. Admins only.');
    return redirectToLogin();
  }

  const movieSelect = document.getElementById('movieSelect') as HTMLSelectElement;
  const roomSelect = document.getElementById('roomSelect') as HTMLSelectElement;
  const dateInput = document.getElementById('date') as HTMLInputElement;
  const timeInput = document.getElementById('time') as HTMLInputElement;
  const priceInput = document.getElementById('price') as HTMLInputElement;
  const addBtn = document.getElementById('addScreening')!;
  const feedback = document.getElementById('feedbackMessage')!;
  const screeningsList = document.getElementById('screeningsList')!;

  // Add a variable to store movies with runtime for lookup
  let moviesWithRuntime: Movie[] = [];

  async function loadMovies() {
    movieSelect.replaceChildren();
    try {
      const res = await fetch(buildApiUrl('/movies/movies/'), {
        headers: { Authorization: `Bearer ${token}` },
      });
      const movies: Movie[] = await res.json();
      if (!Array.isArray(movies)) {
        feedback.textContent = 'Failed to load movies.';
        return;
      }
      moviesWithRuntime = movies; // Store for runtime lookup
      movies.forEach((movie) => {
        const option = document.createElement('option');
        option.value = movie.id;
        option.textContent = movie.title;
        movieSelect.appendChild(option);
      });
    } catch {
      feedback.textContent = 'Error loading movies.';
    }
  }

  async function loadRooms() {
    roomSelect.replaceChildren();
    try {
      const cinemasRes = await fetch(buildApiUrl('admin/admin/cinemas'), {
        headers: { Authorization: `Bearer ${token}` },
      });
      const cinemas = await cinemasRes.json();
      if (!Array.isArray(cinemas) || cinemas.length === 0) {
        feedback.textContent = 'No cinemas found.';
        return;
      }
      const cinemaId = cinemas[0].id;

      const roomsRes = await fetch(buildApiUrl(`admin/admin/cinemas/${cinemaId}/rooms`), {
        headers: { Authorization: `Bearer ${token}` },
      });
      const rooms: Room[] = await roomsRes.json();

      if (!Array.isArray(rooms)) {
        feedback.textContent = 'Failed to load rooms.';
        return;
      }

      rooms.forEach((room) => {
        const option = document.createElement('option');
        option.value = room.id;
        option.textContent = room.name || 'Unknown room';
        roomSelect.appendChild(option);
      });
    } catch {
      feedback.textContent = 'Error loading rooms.';
    }
  }

  addBtn.addEventListener('click', async () => {
    const movieId = movieSelect.value;
    const roomId = roomSelect.value;
    const date = dateInput.value;
    const time = timeInput.value;
    const price = parseFloat(priceInput.value);

    if (!movieId || !roomId || !date || !time) {
      feedback.textContent = 'Please fill in all fields.';
      return;
    }

    const startTime = `${date}T${time}:00`;

    if (isNaN(price)) {
      feedback.textContent = 'Please enter a valid price.';
      return;
    }

    // Lookup movie runtime
    const selectedMovie = moviesWithRuntime.find((m) => m.id === movieId);
    if (
      !selectedMovie ||
      typeof selectedMovie.runtime !== 'number' ||
      isNaN(selectedMovie.runtime)
    ) {
      feedback.textContent = 'Selected movie does not have a valid runtime.';
      return;
    }
    // Calculate end_time
    // Parse string like '2025-06-04T11:30:00' as local time manually
    const [datePart, timePart] = startTime.split('T');
    const [year, month, day] = datePart.split('-').map(Number);
    const [hour, minute] = timePart.split(':').map(Number);

    // Note: month is 0-indexed in JS Date
    const startDateObj = new Date(year, month - 1, day, hour, minute);
    const endDateObj = new Date(startDateObj.getTime() + Math.abs(selectedMovie.runtime) * 60000); // Ensure runtime is positive
    const pad = (n: number) => n.toString().padStart(2, '0');
    const endTime = `${endDateObj.getFullYear()}-${pad(endDateObj.getMonth() + 1)}-${pad(endDateObj.getDate())}T${pad(endDateObj.getHours())}:${pad(endDateObj.getMinutes())}:00`;

    console.log('Selected movie:', selectedMovie);
    console.log('Runtime (minutes):', selectedMovie.runtime);

    const payload = {
      movie_id: movieId,
      room_id: roomId,
      start_time: startTime,
      end_time: endTime, // Correct ISO string, e.g. '2025-06-04T13:35:00'
      price: price,
      status: 'scheduled', // Add status as required by backend
    };
    console.log('Adding screening with payload:', payload);

    try {
      const res = await fetch(buildApiUrl('/admin/admin/showings'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(payload),
      });
      console.log('Add screening response:', res);

      if (!res.ok) {
        const errData = await res.json();
        let msg = 'Failed to add screening.';
        if (errData.detail) {
          if (typeof errData.detail === 'string') {
            msg = errData.detail;
          } else if (Array.isArray(errData.detail)) {
            msg = errData.detail
              .map((e: { msg?: string }) => e.msg || JSON.stringify(e))
              .join('; ');
          } else {
            msg = JSON.stringify(errData.detail);
          }
        }
        feedback.textContent = `${msg}`;
        return;
      }

      feedback.textContent = 'Screening successfully added!';
      dateInput.value = '';
      timeInput.value = '';
      priceInput.value = '';
      await loadScreenings();
    } catch {
      feedback.textContent = 'Network error. Please try again.';
    }
  });

  async function loadScreenings() {
    screeningsList.replaceChildren();

    try {
      // Map movies by local UUID
      const movieRes = await fetch(buildApiUrl('/movies/movies/'), {
        headers: { Authorization: `Bearer ${token}` },
      });
      const movies = await movieRes.json();
      const movieMapByUUID = new Map<string, { title: string; poster_path?: string }>();
      if (Array.isArray(movies)) {
        movies.forEach((movie: { id: string; title: string; poster_path?: string }) => {
          movieMapByUUID.set(movie.id, { title: movie.title, poster_path: movie.poster_path });
        });
      }

      // Get cinema and rooms
      const cinemasRes = await fetch(buildApiUrl('/admin/admin/cinemas'), {
        headers: { Authorization: `Bearer ${token}` },
      });
      const cinemas = await cinemasRes.json();
      if (!Array.isArray(cinemas) || cinemas.length === 0) {
        feedback.textContent = 'No cinemas found.';
        return;
      }
      const cinemaId = cinemas[0].id;

      const roomsRes = await fetch(buildApiUrl(`/admin/admin/cinemas/${cinemaId}/rooms`), {
        headers: { Authorization: `Bearer ${token}` },
      });
      const rooms = await roomsRes.json();
      const roomMap = new Map<string, string>();
      if (Array.isArray(rooms)) {
        rooms.forEach((room: Room) => {
          roomMap.set(room.id, room.name || 'Unknown room');
        });
      }

      // Fetch showings
      const res = await fetch(buildApiUrl('/admin/admin/showings'), {
        headers: { Authorization: `Bearer ${token}` },
      });
      const data = await res.json();
      console.log('Fetched showings:', data);
      if (!Array.isArray(data)) {
        feedback.textContent = 'Unexpected response from server.';
        return;
      }

      // Filter upcoming and sort
      const upcomingShowings = data
        .filter((s: Screening) => new Date(s.start_time) >= new Date())
        .sort((a, b) => new Date(a.start_time).getTime() - new Date(b.start_time).getTime());

      // Group by date
      const grouped: Record<string, Screening[]> = {};
      upcomingShowings.forEach((s) => {
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

          const img = document.createElement('img');
          const movie = movieMapByUUID.get(screening.movie_id);
          if (movie && movie.poster_path) {
            img.src = `https://image.tmdb.org/t/p/w92${movie.poster_path}`;
            img.alt = movie.title;
          } else {
            img.alt = 'No poster';
          }

          const rightContainer = document.createElement('div');
          rightContainer.className = 'screening-info';

          const movieTitle = document.createElement('strong');
          movieTitle.textContent = movie?.title ?? 'Unknown movie';

          const time = document.createElement('p');
          time.textContent = new Date(screening.start_time).toLocaleTimeString([], {
            hour: '2-digit',
            minute: '2-digit',
          });

          const room = document.createElement('p');
          room.textContent = roomMap.get(screening.room_id) ?? screening.room_id;

          rightContainer.appendChild(movieTitle);
          rightContainer.appendChild(time);
          rightContainer.appendChild(room);

          // Price display
          const price = document.createElement('p');
          price.textContent = `Price: €${screening.price.toFixed(2)}`;
          rightContainer.appendChild(price);

          // Edit form container (hidden by default)
          const editContainer = document.createElement('div');
          editContainer.className = 'form-section';
          editContainer.style.display = 'none';

          const errorMsg = document.createElement('div');
          errorMsg.className = 'feedback error';
          editContainer.appendChild(errorMsg);

          const dateLabel = document.createElement('label');
          dateLabel.textContent = 'Date:';
          const dateInputEdit = document.createElement('input');
          dateInputEdit.type = 'date';
          dateInputEdit.value = new Date(screening.start_time).toISOString().split('T')[0];
          editContainer.appendChild(dateLabel);
          editContainer.appendChild(dateInputEdit);

          const timeLabel = document.createElement('label');
          timeLabel.textContent = 'Time:';
          const timeInputEdit = document.createElement('input');
          timeInputEdit.type = 'time';
          timeInputEdit.value = new Date(screening.start_time).toTimeString().slice(0, 5);
          editContainer.appendChild(timeLabel);
          editContainer.appendChild(timeInputEdit);

          const roomLabel = document.createElement('label');
          roomLabel.textContent = 'Room:';
          const roomInputEdit = document.createElement('select');

          (rooms as Room[]).forEach((r: Room) => {
            const option = document.createElement('option');
            option.value = r.id;
            option.textContent = r.name || 'Unknown room';
            if (r.id === screening.room_id) option.selected = true;
            roomInputEdit.appendChild(option);
          });

          editContainer.appendChild(roomLabel);
          editContainer.appendChild(roomInputEdit);

          // Add movie select for edit form
          const movieLabelEdit = document.createElement('label');
          movieLabelEdit.textContent = 'Movie:';
          const movieInputEdit = document.createElement('select');
          moviesWithRuntime.forEach((movie) => {
            const option = document.createElement('option');
            option.value = movie.id;
            option.textContent = movie.title;
            if (movie.id === screening.movie_id) option.selected = true;
            movieInputEdit.appendChild(option);
          });
          editContainer.appendChild(movieLabelEdit);
          editContainer.appendChild(movieInputEdit);

          const priceLabel = document.createElement('label');
          priceLabel.textContent = 'Price:';
          const priceInputEdit = document.createElement('input');
          priceInputEdit.type = 'number';
          priceInputEdit.step = '0.01';
          priceInputEdit.min = '0';
          priceInputEdit.value = screening.price.toFixed(2);
          editContainer.appendChild(priceLabel);
          editContainer.appendChild(priceInputEdit);

          const btnContainer = document.createElement('div');
          btnContainer.style.display = 'flex';
          btnContainer.style.gap = '0.5rem';
          btnContainer.style.marginTop = '1rem';

          const saveBtn = document.createElement('button');
          saveBtn.className = 'btn';
          saveBtn.textContent = 'Save';
          saveBtn.addEventListener('click', async () => {
            errorMsg.textContent = '';

            const newDate = dateInputEdit.value;
            const newTime = timeInputEdit.value;
            const newRoom = roomInputEdit.value;
            const newMovieId = movieInputEdit.value;
            if (!newDate || !newTime || !newRoom || !newMovieId) {
              errorMsg.textContent = 'Please fill all fields';
              return;
            }
            const newDatetime = `${newDate}T${newTime}:00`;

            // Lookup movie runtime for edit
            const selectedMovie = moviesWithRuntime.find((m) => m.id === newMovieId);
            if (
              !selectedMovie ||
              typeof selectedMovie.runtime !== 'number' ||
              isNaN(selectedMovie.runtime)
            ) {
              errorMsg.textContent = 'Selected movie does not have a valid runtime.';
              return;
            }
            const startDateObj = new Date(newDatetime);
            const endDateObj = new Date(
              startDateObj.getTime() + Math.abs(selectedMovie.runtime) * 60000
            ); // Ensure runtime is positive
            const endTime = endDateObj.toISOString().slice(0, 16) + ':00';

            try {
              const res = await fetch(buildApiUrl(`/admin/admin/showings/${screening.id}`), {
                method: 'PUT',
                headers: {
                  Authorization: `Bearer ${token}`,
                  'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                  movie_id: newMovieId,
                  room_id: newRoom,
                  start_time: newDatetime,
                  end_time: endTime,
                  price: parseFloat(priceInputEdit.value),
                }),
              });
              if (res.ok) {
                await loadScreenings();
              } else {
                const errData = await res.json();
                errorMsg.textContent = errData.detail || 'Failed to update screening.';
              }
            } catch {
              errorMsg.textContent = 'Network error. Please try again.';
            }
          });

          const cancelBtn = document.createElement('button');
          cancelBtn.className = 'btn';
          cancelBtn.textContent = 'Cancel';
          cancelBtn.addEventListener('click', () => {
            errorMsg.textContent = '';
            editContainer.style.display = 'none';
          });

          btnContainer.appendChild(saveBtn);
          btnContainer.appendChild(cancelBtn);
          editContainer.appendChild(btnContainer);

          // Actions container
          const actions = document.createElement('div');
          actions.className = 'screening-actions';

          const editBtn = document.createElement('button');
          editBtn.className = 'edit btn';
          editBtn.textContent = 'Edit';
          editBtn.addEventListener('click', () => {
            editContainer.style.display = editContainer.style.display === 'none' ? 'block' : 'none';
          });

          const deleteBtn = document.createElement('button');
          deleteBtn.className = 'delete btn';
          deleteBtn.textContent = 'Delete';
          deleteBtn.addEventListener('click', async () => {
            if (!confirm('Are you sure you want to delete this screening?')) return;

            const delRes = await fetch(buildApiUrl(`/admin/admin/showings/${screening.id}`), {
              method: 'DELETE',
              headers: { Authorization: `Bearer ${token}` },
            });

            if (delRes.ok) loadScreenings();
            else alert('Failed to delete screening.');
          });

          actions.append(editBtn, deleteBtn);

          rightContainer.appendChild(actions);
          rightContainer.appendChild(editContainer);

          card.appendChild(img);
          card.appendChild(rightContainer);

          screeningsList.appendChild(card);
        });
      });
    } catch {
      feedback.textContent = 'Failed to load screenings.';
    }
  }

  function redirectToLogin() {
    window.location.href = '/views/login';
  }

  loadMovies();
  loadRooms();
  loadScreenings();
});
