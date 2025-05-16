from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from uuid import UUID


class MovieBase(BaseModel):
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
    tmdb_id: int


class MovieUpdate(MovieBase):
    title: Optional[str] = None
    tmdb_id: Optional[int] = None


class MovieInDBBase(MovieBase):
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
