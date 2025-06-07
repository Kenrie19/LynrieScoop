# API Reference

LynrieScoop's backend provides a comprehensive RESTful API that serves both the public website and administrative interface. All endpoints return JSON responses and follow REST conventions.

## Base URL

The API base URL is configurable and defaults to: `http://localhost:8000`

## Authentication

Protected endpoints require a valid JWT token in the Authorization header:

```text
Authorization: Bearer <jwt_token>
```

Tokens are obtained by logging in through the `/auth/login` endpoint.

## API Endpoints

### API Endpoints Authentication

#### POST /auth/login

Authenticates a user and returns a JWT token.

**Request Body**:

```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response**:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### POST /auth/register

Registers a new user account.

**Request Body**:

```json
{
  "name": "John Doe",
  "email": "user@example.com",
  "password": "password123"
}
```

**Response**:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Movies

#### GET /movies/

Returns a list of movies in the database.

**Query Parameters**:

- `skip` (optional): Number of records to skip (default: 0)
- `limit` (optional): Maximum number of records to return (default: 100)

#### GET /movies/by_id/{tmdb_id}

Returns detailed information about a specific movie by its TMDB ID.

#### GET /movies/movies/search

Searches for movies in TMDB database.

**Query Parameters**:

- `query` (required): Search query string

### Showings

#### GET /showings/

Returns a list of movie showings.

**Query Parameters**:

- `skip` (optional): Number of records to skip
- `limit` (optional): Maximum number of records to return
- `movie_id` (optional): Filter by movie ID
- `date` (optional): Filter by date (YYYY-MM-DD)

#### POST /showings/

Creates a new movie showing (requires manager role).

**Request Body**:

```json
{
  "movie_id": "uuid-string",
  "room_id": "uuid-string",
  "start_time": "2023-06-01T19:30:00Z",
  "end_time": "2023-06-01T21:45:00Z",
  "is_3d": false,
  "is_imax": false,
  "is_dolby": false,
  "price": 12.50
}
```

#### GET /showings/{showing_id}

Returns detailed information about a specific showing.

#### PUT /showings/{showing_id}

Updates a specific showing (requires manager role).

#### DELETE /showings/{showing_id}

Deletes a specific showing (requires manager role).

### Bookings

#### GET /bookings/

Returns a list of bookings for the current user.

#### POST /bookings/create

Creates a new booking for a specific showing.

**Query Parameters**:

- `screening_id` (required): UUID of the screening/showing to book

**Notes**:
- Requires authentication
- Automatically sends booking confirmation email to the user's registered email address
- Returns booking details including booking ID and reference number

#### GET /bookings/{booking_id}

Returns detailed information about a specific booking.

### Admin

#### GET /admin/bookings

Returns all bookings (requires manager role).

**Query Parameters**:

- `skip` (optional): Number of records to skip
- `limit` (optional): Maximum number of records to return

#### GET /admin/users

Returns all users (requires manager role).

**Query Parameters**:

- `skip` (optional): Number of records to skip
- `limit` (optional): Maximum number of records to return

## Response Status Codes

- `200 OK`: Request succeeded
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions (wrong role)
- `404 Not Found`: Resource not found
- `409 Conflict`: Resource already exists
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Server-side error

## OpenAPI Documentation

A complete OpenAPI specification is available at `/api-docs` when the server is running.
