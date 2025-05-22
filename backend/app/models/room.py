import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.session import Base


class Room(Base):
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
