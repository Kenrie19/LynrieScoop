# Frontend Guide

The LynrieScoop frontend is built with HTML, CSS, and TypeScript. It provides a responsive user interface for browsing movies, viewing showings, and booking tickets, with a separate administrative interface for managers.

## Technology Stack

- **HTML5**: Semantic markup
- **CSS3**: Responsive design with custom styling
- **TypeScript**: Type-safe JavaScript for application logic
- **Nunjucks**: Template rendering for includes and partials

## Directory Structure

```t
frontend/
├── _includes/           # Reusable template components
├── resources/
│   ├── css/             # Stylesheet files
│   ├── images/          # Image assets
│   ├── typescript/      # TypeScript source files
│   └── videos/          # Video assets
└── views/               # HTML view templates
```

## Key Files

- **index.html**: Main landing page
- **_includes/navbar.njk**: Navigation bar template
- **_includes/env.njk**: Environment variables template
- **resources/typescript/config.ts**: Configuration utilities
- **resources/typescript/auth.ts**: Authentication functionality
- **resources/typescript/main.ts**: Main application logic

## Pages and Features

### Public Pages

#### Home Page (`index.html`)

- Hero section with video background
- Trending movies section
- Now playing movies section

#### Movie Details (`views/movie_details.html`)

- Movie information (title, overview, release date, etc.)
- Trailer playback
- Showing schedule
- Book ticket button

#### Now Playing (`views/now_playing.html`)

- List of currently showing movies
- Filter by date
- Quick links to book tickets

#### Login & Registration (`views/login.html` & `views/register.html`)

- User authentication forms
- Validation and error handling
- Redirect based on user role

### User Pages

#### My Movies (`views/my_movies.html`)

- List of booked tickets
- Booking details
- Seat information

#### Ticket Reservation (`views/ticket_reservation.html`)

- Interactive seat selection
- Real-time seat availability updates via MQTT
- Booking confirmation workflow

### Admin Pages

#### Admin Screenings (`views/admin_screenings.html`)

- List of all showings
- Create, edit, and delete showings
- Filter by date, movie, etc.

#### Admin Movie Database (`views/admin_movie_database.html`)

- Search for movies in TMDB
- Import movies to local database
- Edit movie details

## Authentication Flow

1. User submits login credentials through the login form
2. Backend validates credentials and returns JWT token
3. Frontend stores token in cookies
4. Token is included in subsequent API requests
5. User UI is adjusted based on role information in the token

## JavaScript Modules

### `config.ts`

Provides API URL configuration and environment variable handling.

### `auth.ts`

Handles authentication-related functions like login, registration, and token management.

### `cookies.ts`

Utilities for managing cookies and JWT tokens.

### `movie_detail.ts`

Handles the movie detail page functionality, including fetching movie details and showing schedules.

### `admin_screenings.ts`

Admin functionality for managing movie showings and schedules.

### `admin_movie_database.ts`

Admin functionality for searching and managing the movie database.

### `ticket_reservation.ts`

Manages the ticket reservation process, including seat selection and booking confirmation.

## Styling

The application uses custom CSS for styling with a responsive design approach. Key features include:

- Mobile-first responsive design
- Custom movie card components
- Interactive seat selection grid
- Admin dashboard styling
- Dark theme throughout the application
