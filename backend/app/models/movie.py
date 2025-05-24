"""
Movie data models for the LynrieScoop cinema application.
This module defines the ORM model for movies shown in the cinema.
"""

import uuid
from datetime import datetime
from typing import Sequence

from sqlalchemy import Column, DateTime, Float, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import relationship

from app.db.session import Base


class Movie(Base):
    """
    SQLAlchemy ORM model representing a movie in the cinema database.

    This model stores comprehensive information about movies including
    metadata from The Movie Database (TMDB), showing details, and
    associated information like trailers and cast.

    Attributes:
        id (UUID): Primary key, unique identifier for the movie
        tmdb_id (int): Movie ID from The Movie Database (TMDB)
        title (str): The movie title
        overview (str): Plot summary or description
        poster_path (str): URL path to the movie poster image
        backdrop_path (str): URL path to the movie backdrop image
        release_date (datetime): When the movie was released
        runtime (int): Duration of the movie in minutes
        genres (List[str]): List of genre names for the movie
        vote_average (float): Average rating from TMDB (0-10)
        vote_count (int): Number of votes received on TMDB
        director (str): Name of the movie director
        cast (List[str]): List of main cast members
        trailer_url (str): URL to the movie trailer
        status (str): Current status (e.g., "Released", "Coming Soon")
    """

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
