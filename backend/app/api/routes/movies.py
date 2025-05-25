"""
Movie API routes for the LynrieScoop cinema application.

This module defines the REST API endpoints for managing movies,
including CRUD operations and integrations with TMDB for movie data.
"""

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
async def get_movies(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)) -> Any:
    """
    Get list of movies from local database
    """
    result = await db.execute(select(Movie).offset(skip).limit(limit))
    movies = result.scalars().all()
    return movies


@router.get("/by_id/{tmdb_id}", response_model=MovieDetail)
async def get_movie(
    tmdb_id: int,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Retrieve a list of movies with optional filtering and pagination.

    This endpoint retrieves movies from the database, with options to search,
    sort, and paginate the results.

    Args:
        skip: Number of movies to skip (for pagination)
        limit: Maximum number of movies to return
        search: Optional search term to filter movies by title
        sort_by: Sorting criteria (e.g., "popularity.desc", "release_date.asc")
        page: Page number for pagination

    Returns:
        List[MovieSchema]: List of movie objects matching the criteria

    Raises:
        HTTPException: If there's an issue retrieving the movies
    """

    result = await db.execute(select(Movie).filter(Movie.tmdb_id == tmdb_id))
    movie = result.scalars().first()

    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie not found",
        )

    return movie


@router.get("/now_playing", response_model=List[TMDBMovie])
async def get_now_playing_movies(
    page: int = Query(1, ge=1, le=1000),
    sort_by: str = Query("popularity.desc", description="Sort results by specified criteria"),
) -> Any:
    """
    Retrieve a list of movies currently playing in theaters.

    This endpoint fetches the latest movies that are currently in theaters
    from the TMDB API. Results can be paginated and sorted according to
    different criteria like popularity or release date.

    Args:
        page: Page number for pagination (1-1000)
        sort_by: Sorting criteria (e.g., "popularity.desc", "release_date.asc")

    Returns:
        List[TMDBMovie]: List of movie objects currently in theaters

    Raises:
        HTTPException: If there's an error fetching data from TMDB API
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
    Retrieve a list of upcoming movies soon to be in theaters.

    This endpoint fetches movies that are scheduled for release in the near future
    from the TMDB API. Results can be paginated and sorted according to
    different criteria like popularity or release date.

    Args:
        page: Page number for pagination (1-1000)
        sort_by: Sorting criteria (e.g., "popularity.desc", "release_date.asc")

    Returns:
        List[TMDBMovie]: List of upcoming movie objects

    Raises:
        HTTPException: If there's an error fetching data from TMDB API
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
    Retrieve a list of currently popular movies.

    This endpoint fetches movies that are currently most popular based on
    TMDB metrics, which include factors like view count, ratings, and
    recent activity. Results can be paginated and sorted.

    Args:
        page: Page number for pagination (1-1000)
        sort_by: Sorting criteria (e.g., "popularity.desc", "release_date.asc")

    Returns:
        List[TMDBMovie]: List of popular movie objects

    Raises:
        HTTPException: If there's an error fetching data from TMDB API
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
    Retrieve a list of highest-rated movies.

    This endpoint fetches movies with the highest user ratings from the TMDB API.
    These represent films that have been consistently well-reviewed and rated
    by the TMDB user community. Results can be paginated and sorted.

    Args:
        page: Page number for pagination (1-1000)
        sort_by: Sorting criteria (e.g., "popularity.desc", "vote_average.desc")

    Returns:
        List[TMDBMovie]: List of top-rated movie objects

    Raises:
        HTTPException: If there's an error fetching data from TMDB API
    """
    collection = tmdb.Movies()
    top_rated = collection.top_rated(page=page, sort_by=sort_by)
    return top_rated["results"]


@router.get("/search", response_model=List[TMDBMovie])
async def search_movies(
    query: str = Query(..., min_length=1),
    page: int = Query(1, ge=1, le=1000),
) -> Any:
    """
    Search for movies in TMDB
    """
    try:
        collection = tmdb.Search()
        search_results = collection.movie(query=query, page=page)

        if not search_results.get("results"):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No movies found",
            )
        return search_results["results"]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, detail=f"TMDB API error: {str(e)}"
        )


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
