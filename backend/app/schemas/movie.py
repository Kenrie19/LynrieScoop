"""
Movie schema definitions for the LynrieScoop cinema application.

This module provides Pydantic models for movie data validation, serialization,
and documentation in the API. These schemas define the structure of request
and response data for movie-related API endpoints.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel


class MovieBase(BaseModel):
    """
    Base movie schema with common attributes.

    This schema includes the core attributes shared across all movie schemas,
    and serves as a base class for more specific movie schemas.

    Attributes:
        title (str): The movie title
        overview (str, optional): Plot summary or description
        poster_path (str, optional): URL path to the movie poster image
        backdrop_path (str, optional): URL path to the movie backdrop image
        release_date (datetime, optional): When the movie was released
        runtime (int, optional): Duration of the movie in minutes
        genres (List[str], optional): List of genre names for the movie
        vote_average (float, optional): Average rating from TMDB (0-10)
        vote_count (int, optional): Number of votes received on TMDB
    """

    title: str
    overview: Optional[str] = None
    poster_path: Optional[str] = None
    backdrop_path: Optional[str] = None
    release_date: Optional[datetime] = None
    runtime: Optional[int] = None
    genres: Optional[List[str]] = None
    vote_average: Optional[float] = None
    vote_count: Optional[int] = None


class MovieCreate(MovieBase):
    """
    Schema for creating a new movie.

    Extends MovieBase with required fields for movie creation.

    Attributes:
        tmdb_id (int): The Movie Database ID for the movie
    """

    tmdb_id: int


class MovieUpdate(MovieBase):
    """
    Schema for updating an existing movie.

    Makes all fields optional for partial updates.

    Attributes:
        tmdb_id (int, optional): The Movie Database ID for the movie
    """

    tmdb_id: Optional[int] = None


class MovieInDBBase(MovieBase):
    """
    Base schema for movies as stored in the database.

    Includes database-specific fields that aren't in the base model.

    Attributes:
        id (UUID): Unique identifier in our database
        tmdb_id (int): The Movie Database ID for the movie
        created_at (datetime): When the movie record was created
    """

    id: UUID
    tmdb_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Movie(MovieInDBBase):
    """Movie data returned to clients"""

    pass


class MovieDetail(Movie):
    """Movie data with additional details"""

    pass


class TMDBMovie(BaseModel):
    """Movie data from TMDB API"""

    id: int
    title: str
    overview: Optional[str] = None
    poster_path: Optional[str] = None
    backdrop_path: Optional[str] = None
    release_date: Optional[str] = None
    runtime: Optional[int] = None
    genres: Optional[List[dict]] = None
    vote_average: Optional[float] = None
    vote_count: Optional[int] = None
    director: Optional[str] = None
    cast: Optional[List[str]] = None
    trailer_url: Optional[str] = None
    status: Optional[str] = None
