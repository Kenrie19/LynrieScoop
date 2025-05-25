"""
Showing data model for the LynrieScoop cinema application.

This module defines the ORM model for movie showings, representing
scheduled screenings of movies in specific cinema rooms.
"""

import uuid
from datetime import datetime
from typing import Literal

from sqlalchemy import Boolean, Column, DateTime, Enum, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.session import Base


class Showing(Base):
    """
    SQLAlchemy ORM model representing a movie showing in the cinema system.

    This model stores detailed information about scheduled movie screenings,
    including the movie being shown, the room it's showing in, timing details,
    special formats, pricing, and current status.

    Attributes:
        id (UUID): Primary key, unique identifier for the showing
        movie_id (UUID): Foreign key to the movies table
        room_id (UUID): Foreign key to the rooms table
        start_time (datetime): When the movie showing starts
        end_time (datetime): When the movie showing ends
        is_3d (bool): Whether this showing is in 3D format
        is_imax (bool): Whether this showing is in IMAX format
        is_dolby (bool): Whether this showing is in Dolby format
        price (float): Base ticket price for this showing
        status (str): Current status of the showing:
            - "scheduled": The showing is scheduled to occur
            - "cancelled": The showing has been cancelled
            - "completed": The showing has already happened
        created_at (datetime): When the showing record was created
        updated_at (datetime): When the showing record was last updated

    Relationships:
        movie: The movie being shown
        room: The room where the movie is showing
        bookings: All bookings made for this showing
    """

    __tablename__ = "showings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    movie_id = Column(UUID(as_uuid=True), ForeignKey("movies.id"), nullable=False)
    room_id = Column(UUID(as_uuid=True), ForeignKey("rooms.id"), nullable=False)
    start_time = Column(DateTime, nullable=False, index=True)
    end_time = Column(DateTime, nullable=False)
    is_3d = Column(Boolean, default=False)
    is_imax = Column(Boolean, default=False)
    is_dolby = Column(Boolean, default=False)
    price = Column(Float, nullable=False)
    status: Column[Literal["scheduled", "cancelled", "completed"]] = Column(
        Enum("scheduled", "cancelled", "completed", name="showing_status"),
        default="scheduled",
        nullable=False,
    )
    bookings_count = Column(Integer, default=0, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    movie = relationship("Movie", back_populates="showings")
    room = relationship("Room", back_populates="showings")
    bookings = relationship("Booking", back_populates="showing", cascade="all, delete-orphan")
    seat_reservations = relationship(
        "SeatReservation", back_populates="showing", cascade="all, delete-orphan"
    )
