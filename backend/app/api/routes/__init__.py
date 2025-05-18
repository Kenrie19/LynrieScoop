# Import routers here for easier access
from app.api.routes import admin, auth, bookings, cinemas, movies, showings, users

# Re-export routers with consistent naming
admin_router = admin.router
auth_router = auth.router
bookings_router = bookings.router
cinemas_router = cinemas.router
movies_router = movies.router
showings_router = showings.router
users_router = users.router
