"""
SeatReservation data model for the LynrieScoop cinema application.

This module defines the ORM model for seat reservations, which track the
status of individual seats for specific movie showings and bookings.
"""

import uuid
from datetime import datetime
from typing import Literal

from sqlalchemy import Column, DateTime, Enum, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.session import Base


class SeatReservation(Base):
    """
    SQLAlchemy ORM model representing a seat reservation for a movie showing.

    This model tracks the status of each seat for each showing, connecting
    seats to bookings and managing the reservation lifecycle. It supports
    temporary holds, confirmed bookings, and availability tracking.

    Attributes:
        id (UUID): Primary key, unique identifier for the reservation
        booking_id (UUID): Foreign key to the booking this reservation belongs to
        showing_id (UUID): Foreign key to the movie showing
        seat_id (UUID): Foreign key to the specific seat being reserved
        row (str): Row identifier, duplicated from the seat for quick access
        number (int): Seat number, duplicated from the seat for quick access
        price (float): Price for this specific seat (may vary by seat type)
        status (str): Current status of the reservation:
            - "available": Seat is available for booking
            - "selected": Seat is temporarily selected by a user
            - "reserved": Seat is reserved but not yet confirmed
            - "booked": Seat is fully booked and confirmed
        created_at (datetime): When the reservation was created
        updated_at (datetime): When the reservation was last updated
        expires_at (datetime): When a temporary reservation expires

    Relationships:
        booking: The booking this reservation is part of
        showing: The showing this reservation is for
        seat: The specific seat being reserved
    """

    __tablename__ = "seat_reservations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    booking_id = Column(UUID(as_uuid=True), ForeignKey("bookings.id"), nullable=False)
    showing_id = Column(UUID(as_uuid=True), ForeignKey("showings.id"), nullable=False)
    seat_id = Column(UUID(as_uuid=True), ForeignKey("seats.id"), nullable=False)
    row = Column(String, nullable=False)  # Row identifier (A, B, C, etc.)
    number = Column(Integer, nullable=False)  # Seat number in the row
    price = Column(Float, nullable=False)
    status: Column[Literal["available", "selected", "reserved", "booked"]] = Column(
        Enum("available", "selected", "reserved", "booked", name="seat_status"),
        default="available",
        nullable=False,
    )

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)  # For temporary reservations

    # Relationships
    booking = relationship("Booking", back_populates="seat_reservations")
    showing = relationship("Showing", back_populates="seat_reservations")
    seat = relationship("Seat", back_populates="reservations")
