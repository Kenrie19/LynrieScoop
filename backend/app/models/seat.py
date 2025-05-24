"""
Seat data model for the LynrieScoop cinema application.

This module defines the ORM model for individual seats within cinema rooms,
allowing for detailed seat management and reservations.
"""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.session import Base


class Seat(Base):
    """
    SQLAlchemy ORM model representing an individual seat in a cinema room.

    This model stores detailed information about each seat, including its
    position, type, accessibility features, and status. Each seat belongs
    to a specific room and can be reserved for showings.

    Attributes:
        id (UUID): Primary key, unique identifier for the seat
        room_id (UUID): Foreign key to the room this seat belongs to
        row (str): Row identifier (e.g., "A", "B", "C")
        number (int): Seat number within the row
        seat_type (str): Type of seat ("standard", "premium", "VIP", etc.)
        is_accessible (bool): Whether this seat is wheelchair accessible
        is_active (bool): Whether the seat is currently available for booking
        created_at (datetime): When the seat record was created
        updated_at (datetime): When the seat record was last updated

    Relationships:
        room: The room this seat belongs to
        seat_reservations: History of reservations for this seat
    """

    __tablename__ = "seats"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    room_id = Column(UUID(as_uuid=True), ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False)
    row = Column(String(5), nullable=False)  # e.g., "A", "B", "C", etc.
    number = Column(Integer, nullable=False)  # e.g., 1, 2, 3, etc.
    seat_type = Column(
        String(20), nullable=False, default="standard"
    )  # standard, premium, VIP, etc.
    is_accessible = Column(Boolean, default=False)  # wheelchair accessible
    is_active = Column(Boolean, default=True)  # seat can be deactivated for maintenance

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    room = relationship("Room", back_populates="seats")
    reservations = relationship(
        "SeatReservation", back_populates="seat", cascade="all, delete-orphan"
    )

    class Config:
        from_attributes = True

    def __repr__(self) -> str:
        return f"Seat(id={self.id}, room_id={self.room_id}, row={self.row}, number={self.number})"
