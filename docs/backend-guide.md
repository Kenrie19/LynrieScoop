# Backend Guide

The LynrieScoop backend is built with FastAPI (Python) and provides a robust API service with database persistence, authentication, and real-time messaging capabilities.

## Technology Stack

- **FastAPI**: Fast and modern Python web framework
- **SQLAlchemy**: SQL toolkit and Object-Relational Mapping (ORM)
- **Pydantic**: Data validation and settings management
- **MQTT**: Message Queuing Telemetry Transport for real-time updates
- **JWT**: JSON Web Tokens for authentication
- **PostgreSQL**: Relational database management system

## Directory Structure

```t
backend/
├── app/
│   ├── api/
│   │   └── routes/        # API endpoint definitions
│   ├── core/              # Core functionality and configuration
│   ├── db/                # Database initialization and session management
│   ├── models/            # SQLAlchemy ORM models
│   └── schemas/           # Pydantic validation schemas
├── docs/                  # Documentation
└── main.py                # Application entry point
```

## Key Components

### Main Application (`main.py`)

The entry point of the application. It initializes FastAPI, sets up middleware (CORS, Trusted Host), configures MQTT, and registers API routers.

### Configuration (`app/core/config.py`)

Defines application settings using Pydantic's BaseSettings. Handles environment variable loading, database URLs, MQTT broker settings, etc.

### Database (`app/db/`)

- **session.py**: Database connection setup
- **init_db.py**: Database initialization and migration
- **seed_data.py**: Initial data seeding for testing

### Models (`app/models/`)

SQLAlchemy ORM models representing the database schema:

- **User**: User accounts with role-based permissions
- **Movie**: Movie information integrated with TMDB data
- **Showing**: Scheduled movie screenings
- **Booking**: Ticket bookings made by users
- **Room**: Cinema rooms/theaters
- **Seat**: Individual seats within rooms
- **SeatReservation**: Links seats to bookings for specific showings

### API Routes (`app/api/routes/`)

Organized by resource type:

- **auth.py**: Authentication endpoints (login, register)
- **movies.py**: Movie-related endpoints
- **showings.py**: Showing-related endpoints
- **bookings.py**: Booking-related endpoints
- **admin.py**: Admin-only endpoints

### MQTT Client (`app/core/mqtt_client.py`)

Handles real-time messaging through MQTT for seat status updates and booking notifications.

## Data Models

### User

```python
class User(Base):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum("user", "manager", name="user_role"), default="user", nullable=False)
    is_active = Column(Boolean, default=True)
    avatar = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

### Movie

```python
class Movie(Base):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tmdb_id = Column(Integer, unique=True, index=True)
    title = Column(String, nullable=False, index=True)
    overview = Column(Text, nullable=True)
    poster_path = Column(String, nullable=True)
    backdrop_path = Column(String, nullable=True)
    release_date = Column(DateTime, nullable=True)
    runtime = Column(Integer, nullable=True)
    genres = Column(ARRAY(String), nullable=True)
    vote_average = Column(Float, nullable=True)
    vote_count = Column(Integer, nullable=True)
    director = Column(String, nullable=True)
    cast = Column(ARRAY(String), nullable=True)
    trailer_url = Column(String, nullable=True)
    status = Column(String, nullable=True, default="Released")
```

### Showing

```python
class Showing(Base):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    movie_id = Column(UUID(as_uuid=True), ForeignKey("movies.id"), nullable=False)
    room_id = Column(UUID(as_uuid=True), ForeignKey("rooms.id"), nullable=False)
    start_time = Column(DateTime, nullable=False, index=True)
    end_time = Column(DateTime, nullable=False)
    is_3d = Column(Boolean, default=False)
    is_imax = Column(Boolean, default=False)
    is_dolby = Column(Boolean, default=False)
    price = Column(Float, nullable=False)
    status = Column(
        Enum("scheduled", "cancelled", "completed", name="showing_status"),
        default="scheduled",
        nullable=False,
    )
    bookings_count = Column(Integer, default=0, nullable=False)
```

## Authentication Flow

1. User submits credentials to `/auth/login` or `/auth/register`
2. Backend validates credentials and creates/retrieves user
3. JWT token is generated with user info and role
4. Token is returned to client for subsequent API requests
5. Protected endpoints validate token and check user role

## MQTT Integration

The backend uses MQTT for real-time updates:

- Connects to the MQTT broker on application startup
- Publishes messages when seats are reserved/released
- Subscribes to seat status updates for real-time UI updates
- Handles booking confirmations through MQTT messages

## Error Handling

The backend implements standardized error handling:

- HTTP status codes for different error types
- Structured error responses with detailed messages
- Validation errors using Pydantic schemas
- Exception handlers for common error scenarios

## Email Notifications

The backend supports sending email notifications for important events:

- **Booking Confirmations**: Automatically sends a HTML-formatted email when a booking is successfully created
- **Configuration**: Email settings are defined in environment variables (SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD)
- **Implementation**: Uses Python's `smtplib` and `email.mime` packages for creating and sending emails
- **Error Handling**: Gracefully handles email sending failures without affecting the booking process
