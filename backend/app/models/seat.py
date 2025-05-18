import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.session import Base


class Seat(Base):
    """
    Represents a seat in a cinema room
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
