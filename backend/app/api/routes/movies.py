from typing import Any, List, Optional

import tmdbsimple as tmdb
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.config import settings
from app.core.security import get_current_manager_user
from app.db.session import get_db
from app.models.movie import Movie
from app.models.room import Room
from app.models.showing import Showing
from app.models.user import User
from app.schemas.movie import Movie as MovieSchema
from app.schemas.movie import MovieCreate, MovieDetail, TMDBMovie

tmdb.API_KEY = settings.TMDB_API_KEY


router = APIRouter(prefix="/movies", tags=["movies"])


@router.get("/", response_model=List[MovieSchema])
async def get_movies(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    sort_by: str = "popularity.desc",
    page: int = 1,
) -> Any:
    """
    Get list of movies from TMDB API
    """
    collection = tmdb.Movies()
    movies = collection.popular(page=page, sort_by=sort_by)
    if not movies["results"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No movies found",
        )
    return movies["results"]


@router.get("/now_playing", response_model=List[TMDBMovie])
async def get_now_playing_movies(
    page: int = Query(1, ge=1, le=1000),
    sort_by: str = Query("popularity.desc", description="Sort results by specified criteria"),
) -> Any:
    """
    Get movies currently in theaters from TMDB
    """
    collection = tmdb.Movies()
    now_playing = collection.now_playing(page=page, sort_by=sort_by)
    return now_playing["results"]


@router.get("/upcoming", response_model=List[TMDBMovie])
async def get_upcoming_movies(
    page: int = Query(1, ge=1, le=1000),
    sort_by: str = Query("popularity.desc", description="Sort results by specified criteria"),
) -> Any:
    """
    Get upcoming movies from TMDB
    """
    collection = tmdb.Movies()
    upcoming = collection.upcoming(page=page, sort_by=sort_by)
    return upcoming["results"]


@router.get("/popular", response_model=List[TMDBMovie])
async def get_popular_movies(
    page: int = Query(1, ge=1, le=1000),
    sort_by: str = Query("popularity.desc", description="Sort results by specified criteria"),
) -> Any:
    """
    Get popular movies from TMDB
    """
    collection = tmdb.Movies()
    popular = collection.popular(page=page, sort_by=sort_by)
    return popular["results"]


@router.get("/top_rated", response_model=List[TMDBMovie])
async def get_top_rated_movies(
    page: int = Query(1, ge=1, le=1000),
    sort_by: str = Query("popularity.desc", description="Sort results by specified criteria"),
) -> Any:
    """
    Get top rated movies from TMDB
    """
    collection = tmdb.Movies()
    top_rated = collection.top_rated(page=page, sort_by=sort_by)
    return top_rated["results"]


@router.get("/search", response_model=List[TMDBMovie])
async def search_movies(
    query: str = Query(..., min_length=1),
    page: int = Query(1, ge=1, le=1000),
    sort_by: str = Query("popularity.desc", description="Sort results by specified criteria"),
) -> Any:
    """
    Search for movies in TMDB
    """
    collection = tmdb.Search()
    search_results = collection.movie(query=query, page=page, sort_by=sort_by)
    if not search_results["results"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No movies found",
        )
    return search_results["results"]


@router.get("/{movie_id}", response_model=MovieDetail)
async def get_movie(
    movie_id: int,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get details for a specific movie
    """
    collection = tmdb.Movies(movie_id)
    movie = collection.info()
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie not found",
        )
    return movie


@router.get("/tmdb/{tmdb_id}", response_model=TMDBMovie)
async def get_movie_from_tmdb(
    tmdb_id: int,
) -> Any:
    """
    Get a movie from TMDB by its ID
    """
    collection = tmdb.Movies(tmdb_id)
    movie = collection.info()
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie not found",
        )
    return movie


@router.post("/", response_model=MovieSchema, status_code=status.HTTP_201_CREATED)
async def create_movie(
    movie_data: MovieCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_manager_user),
) -> Any:
    """
    Create a new movie (admin only)
    """
    # Check if movie with this TMDB ID already exists
    result = await db.execute(select(Movie).filter(Movie.tmdb_id == movie_data.tmdb_id))
    if result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Movie with this TMDB ID already exists",
        )

    # Create new movie
    movie = Movie(**movie_data.dict())
    db.add(movie)
    await db.commit()
    await db.refresh(movie)

    return movie


@router.get("/showings", response_model=List[dict])
async def get_movie_showings(
    movie_id: int = Query(..., description="TMDB ID of the movie"),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get all showings for a specific movie
    """
    # First get the movie from our database
    result = await db.execute(select(Movie).filter(Movie.tmdb_id == movie_id))
    movie = result.scalars().first()

    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie not found in the database",
        )

    # Query showings with joined information about rooms
    query = (
        select(
            Showing.id,
            Showing.movie_id,
            Showing.start_time,
            Showing.end_time,
            Showing.price,
            Showing.status,
            Room.id.label("room_id"),
            Room.name.label("room_name"),
        )
        .select_from(Showing)
        .join(Room, Showing.room_id == Room.id)
        .filter(Showing.movie_id == movie.id)
        .filter(Showing.status == "scheduled")
    )

    result = await db.execute(query)
    showings = result.all()

    # Convert to list of dictionaries
    showings_list = [
        {
            "id": str(showing.id),
            "movie_id": int(movie_id),  # Use TMDB ID for frontend consistency
            "room_id": str(showing.room_id),
            "room_name": showing.room_name,
            "start_time": showing.start_time.isoformat(),
            "end_time": showing.end_time.isoformat(),
            "price": float(showing.price),
        }
        for showing in showings
    ]

    return showings_list
