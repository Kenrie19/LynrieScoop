from sqlalchemy import Column, ForeignKey, DateTime, Float, String, Integer, Enum
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from app.db.session import Base


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    showing_id = Column(UUID(as_uuid=True), ForeignKey("showings.id"), nullable=False)
    booking_number = Column(String, unique=True, nullable=False, index=True)
    total_price = Column(Float, nullable=False)
    status = Column(
        Enum("pending", "confirmed", "cancelled", "completed", name="booking_status"),
        default="pending",
        nullable=False,
    )
    payment_method = Column(String, nullable=True)
    payment_id = Column(String, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", backref="bookings")
    showing = relationship("Showing", back_populates="bookings")
    seat_reservations = relationship(
        "SeatReservation", back_populates="booking", cascade="all, delete-orphan"
    )
