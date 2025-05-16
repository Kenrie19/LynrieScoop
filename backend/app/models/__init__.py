"""
Models package initialization.
Import order is important for SQLAlchemy relationships to resolve correctly.
"""

# Import models in order of dependency
from app.models.cinema import Cinema
from app.models.room import Room
from app.models.seat import Seat
from app.models.movie import Movie
from app.models.showing import Showing
from app.models.user import User
from app.models.booking import Booking
from app.models.seat_reservation import SeatReservation

# This ensures all models are loaded when importing from app.models
__all__ = [
    "Cinema",
    "Room",
    "Seat",
    "Movie",
    "Showing",
    "User",
    "Booking",
    "SeatReservation",
]
