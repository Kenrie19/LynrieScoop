from typing import Any, Dict, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from app.db.session import get_db
from app.models.movie import Movie
from app.models.showing import Showing
from app.schemas.movie import Movie as MovieSchema

router = APIRouter(prefix="/showings", tags=["showings"])


@router.get("/", response_model=List[Dict])
async def get_showings(
    movie_id: int = Query(..., description="TMDB ID of the movie"),
    db: AsyncSession = Depends(get_db),
) -> Any:
    result = await db.execute(select(Movie).filter(Movie.tmdb_id == movie_id))
    movie = result.scalars().first()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    result = await db.execute(
        select(Showing)
        .options(joinedload(Showing.room))
        .filter(Showing.movie_id == movie.id)
        .filter(Showing.status == "scheduled")
    )
    showings = result.scalars().all()

    return [
        {
            "id": str(s.id),
            "movie_id": movie_id,
            "room_id": str(s.room.id) if s.room else None,
            "room_name": s.room.name if s.room else None,
            "start_time": s.start_time.isoformat(),
            "end_time": s.end_time.isoformat() if s.end_time else None,
            "price": s.price,
        }
        for s in showings
    ]


@router.get("/{id}/tickets", response_model=Dict)
async def get_showing_tickets(
    id: UUID,
    db: AsyncSession = Depends(get_db),
) -> Any:
    result = await db.execute(
        select(Showing)
        .options(joinedload(Showing.room), joinedload(Showing.movie))
        .filter(Showing.id == id)
    )
    showing = result.scalars().first()
    if not showing:
        raise HTTPException(status_code=404, detail="Showing not found")

    # Fetch bookings_count using SQL expression
    bookings_count_result = await db.execute(
        select(Showing.bookings_count).where(Showing.id == showing.id)
    )
    bookings_count = bookings_count_result.scalar() or 0

    return {
        "showing_id": str(showing.id),
        "total_capacity": showing.room.capacity,
        "available_tickets": showing.room.capacity - bookings_count,
        "price": showing.price,
        "movie_title": showing.movie.title if showing.movie else None,
        "movie_id": showing.movie.tmdb_id if showing.movie else None,
        "start_time": showing.start_time.isoformat() if showing.start_time else None,
        "end_time": showing.end_time.isoformat() if showing.end_time else None,
        "room_name": showing.room.name if showing.room else None,
        "movie_poster": showing.movie.poster_path if showing.movie else None,
        "movie_overview": showing.movie.overview if showing.movie else None,
    }


@router.get("/{id}/seats", response_model=List[Dict])
async def get_showing_seats(
    id: UUID,
    db: AsyncSession = Depends(get_db),
) -> Any:
    result = await db.execute(
        select(Showing).options(joinedload(Showing.room)).filter(Showing.id == id)
    )
    showing = result.scalars().first()
    if not showing:
        raise HTTPException(status_code=404, detail="Showing not found")

    rows = ["A", "B", "C", "D", "E", "F", "G", "H"]
    seats_per_row = 12
    seats = []

    for row in rows:
        for number in range(1, seats_per_row + 1):
            is_accessible = row == "H" and number in [1, 2]
            status = "available"
            if (row == "D" and number in [6, 7]) or (row == "E" and number in [6, 7]):
                status = "booked"
            seats.append(
                {
                    "id": f"{row}{number}",
                    "row": row,
                    "number": number,
                    "status": status,
                    "isAccessible": is_accessible,
                    "price": 15.0 if is_accessible else 12.0,
                }
            )

    return seats


@router.get("/now-playing", response_model=List[MovieSchema])
async def get_now_playing_from_local(db: AsyncSession = Depends(get_db)) -> Any:
    """
    Get all movies that currently have at least one scheduled showing
    """

    result = await db.execute(
        select(Movie).join(Showing).filter(Showing.status == "scheduled").distinct()
    )
    movies = result.scalars().all()
    return movies
