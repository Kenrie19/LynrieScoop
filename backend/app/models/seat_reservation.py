from sqlalchemy import Column, ForeignKey, DateTime, Float, String, Integer, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from app.db.session import Base


class SeatReservation(Base):
    __tablename__ = "seat_reservations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    booking_id = Column(UUID(as_uuid=True), ForeignKey("bookings.id"), nullable=False)
    showing_id = Column(UUID(as_uuid=True), ForeignKey("showings.id"), nullable=False)
    seat_id = Column(UUID(as_uuid=True), ForeignKey("seats.id"), nullable=False)
    row = Column(String, nullable=False)  # Row identifier (A, B, C, etc.)
    number = Column(Integer, nullable=False)  # Seat number in the row
    price = Column(Float, nullable=False)
    status = Column(
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
