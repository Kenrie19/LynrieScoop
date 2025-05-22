import uuid
from datetime import datetime
from typing import Sequence

from sqlalchemy import Column, DateTime, Float, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import relationship

from app.db.session import Base


class Movie(Base):
    __tablename__ = "movies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tmdb_id = Column(Integer, unique=True, index=True)
    title = Column(String, nullable=False, index=True)
    overview = Column(Text, nullable=True)
    poster_path = Column(String, nullable=True)
    backdrop_path = Column(String, nullable=True)
    release_date = Column(DateTime, nullable=True)
    runtime = Column(Integer, nullable=True)  # in minutes
    genres: Column[Sequence[str]] = Column(ARRAY(String), nullable=True)
    vote_average = Column(Float, nullable=True)
    vote_count = Column(Integer, nullable=True)
    director = Column(String, nullable=True)
    cast: Column[Sequence[str]] = Column(ARRAY(String), nullable=True)
    trailer_url = Column(String, nullable=True)
    status = Column(String, nullable=True, default="Released")

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    showings = relationship("Showing", back_populates="movie", cascade="all, delete-orphan")
