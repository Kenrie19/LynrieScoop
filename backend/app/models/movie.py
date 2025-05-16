from sqlalchemy import Column, String, Integer, Float, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

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
    genres = Column(ARRAY(String), nullable=True)
    vote_average = Column(Float, nullable=True)
    vote_count = Column(Integer, nullable=True)
    director = Column(String, nullable=True)
    cast = Column(ARRAY(String), nullable=True)
    trailer_url = Column(String, nullable=True)
    status = Column(String, nullable=True, default="Released")

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    showings = relationship(
        "Showing", back_populates="movie", cascade="all, delete-orphan"
    )
