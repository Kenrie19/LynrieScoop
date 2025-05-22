import uuid
from datetime import datetime
from typing import Literal

from sqlalchemy import Boolean, Column, DateTime, Enum, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.session import Base


class Showing(Base):
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
