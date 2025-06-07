"""
Room data model for the LynrieScoop cinema application.

This module defines the ORM model for cinema screening rooms, representing
the auditoriums where movies are shown within a cinema.
"""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.session import Base


class Room(Base):
    """
    SQLAlchemy ORM model representing a screening room in a cinema.

    This model stores information about individual screening rooms/auditoriums,
    including their capacity, special features, and which cinema they belong to.

    Attributes:
        id (UUID): Primary key, unique identifier for the room
        name (str): Name or number of the screening room
        capacity (int): Maximum number of seats in the room
        has_3d (bool): Whether the room can show 3D movies
        has_imax (bool): Whether the room has IMAX capabilities
        has_dolby (bool): Whether the room has Dolby sound system
        cinema_id (UUID): Foreign key to the cinema this room belongs to
        created_at (datetime): When the room record was created
        updated_at (datetime): When the room record was last updated

    Relationships:
        cinema: The cinema this room belongs to
        showings: Movie showings scheduled in this room
        seats: Individual seats within this room
    """

    __tablename__ = "rooms"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    capacity = Column(Integer, nullable=False)
    has_3d = Column(Boolean, default=False)
    has_imax = Column(Boolean, default=False)
    has_dolby = Column(Boolean, default=False)
    cinema_id = Column(UUID(as_uuid=True), ForeignKey("cinemas.id"), nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    cinema = relationship("Cinema", back_populates="rooms")
    showings = relationship("Showing", back_populates="room", cascade="all, delete-orphan")
    seats = relationship("Seat", back_populates="room", cascade="all, delete-orphan")
