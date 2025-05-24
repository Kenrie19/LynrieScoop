from datetime import datetime
from typing import Any, List
from uuid import UUID

import tmdbsimple as tmdb
from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from app.core.config import settings
from app.core.security import get_current_user
from app.db.session import get_db
from app.models.movie import Movie
from app.models.room import Room
from app.models.showing import Showing
from app.models.user import User

tmdb.API_KEY = settings.TMDB_API_KEY

router = APIRouter(prefix="/showings", tags=["showings"])


@router.get("/", response_model=List[dict])
async def get_showing(
    movie_id: int = Query(
        ..., title="Movie ID", description="TMDB ID of the movie to get showings for"
    ),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Retrieve all showings for a specific movie by its TMDB ID.

    This endpoint returns details about all scheduled showings for a particular movie,
    identified by its TMDB ID. The response includes showing times, room information,
    and ticket availability.

    Args:
        movie_id: TMDB ID of the movie to get showings for
        db: Database session dependency

    Returns:
        List[dict]: List of showing objects with details including times, room, and availability

    Raises:
        HTTPException: If there's an error retrieving the showings
    """
    # First get the movie from our database using the TMDB ID
    """
    Get all planned screenings
    """
    result = await db.execute(
        select(Showing)
        .options(joinedload(Showing.movie), joinedload(Showing.room))
        .order_by(Showing.start_time)
    )
    showings = result.scalars().all()

    screenings_list = []
    for showing in showings:
        # Get the movie details from TMDB if available
        movie_details = None
        if showing.movie and showing.movie.tmdb_id:
            try:
                collection = tmdb.Movies(showing.movie.tmdb_id)
                movie_details = collection.info()
            except Exception:
                # If TMDB API fails, continue with local data
                pass

        available_tickets = showing.room.capacity - showing.bookings_count if showing.room else 0

        screenings_list.append(
            {
                "id": str(showing.id),
                "movie_id": showing.movie.tmdb_id if showing.movie else None,
                "movie_title": (
                    showing.movie.title
                    if showing.movie
                    else (movie_details.get("title") if movie_details else "Unknown")
                ),
                "start_time": showing.start_time.isoformat(),
                "end_time": showing.end_time.isoformat() if showing.end_time else None,
                "room": showing.room.name if showing.room else "Unknown",
                "available_tickets": available_tickets,
                "price": showing.price,
            }
        )
    return showings


@router.get("/seats/{showing_id}", response_model=List[dict])
async def get_showing_seats(
    showing_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Retrieve all seats and their availability status for a specific showing.

    This endpoint returns details about each seat in the room for a particular showing,
    including seat position (row/number), accessibility features, and current booking status
    (available, reserved, or booked). This is used for the seat selection UI.

    Args:
        showing_id: UUID of the showing to get seats for
        db: Database session dependency

    Returns:
        List[dict]: List of seat objects with position and status information

    Raises:
        HTTPException: If the showing or room information is not found
    """
    # First, verify the showing exists
    result = await db.execute(select(Showing).filter(Showing.id == showing_id))
    showing = result.scalars().first()

    if not showing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Showing not found",
        )

    # Query to get all seats for the room with their booked status
    query = (
        select(
            Room.id.label("room_id"),
            Room.name.label("room_name"),
        )
        .select_from(Showing)
        .join(Room, Showing.room_id == Room.id)
        .filter(Showing.id == showing_id)
    )

    result = await db.execute(query)
    room_data = result.first()

    if not room_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room information not found",
        )

    # In a real implementation, you would get the actual seats and their status
    # This is a placeholder implementation that returns mock data
    # You would need to query the seats table and join with reservations

    rows = ["A", "B", "C", "D", "E", "F", "G", "H"]
    seats_per_row = 12
    seats = []

    for row in rows:
        for number in range(1, seats_per_row + 1):
            is_accessible = row == "H" and number in [1, 2]
            seat_status = "available"

            # Mock some booked/reserved seats for demonstration
            if (row == "D" and number in [6, 7]) or (row == "E" and number in [6, 7]):
                seat_status = "booked"

            seats.append(
                {
                    "id": f"{row}{number}",
                    "row": row,
                    "number": number,
                    "status": seat_status,
                    "isAccessible": is_accessible,
                    "price": (
                        15.0 if is_accessible else 12.0
                    ),  # Different pricing for accessible seats
                }
            )

    return seats


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_showing(
    movie_id: int = Body(..., description="TMDB Movie ID"),
    room_id: UUID = Body(..., description="Room ID"),
    start_time: datetime = Body(..., description="Start time of the showing"),
    end_time: datetime = Body(..., description="End time of the showing"),
    price: float = Body(..., description="Ticket price"),
    showing_status: str = Body("scheduled", description="Status of the showing"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Create a new movie showing/screening.

    This endpoint allows cinema administrators to create a new showing by specifying
    the movie (via TMDB ID), room, timing, pricing, and initial status. The system
    verifies that there are no scheduling conflicts before creating the showing.

    Args:
        movie_id: TMDB ID of the movie to show
        room_id: UUID of the room where the showing will take place
        start_time: Date and time when the showing starts
        end_time: Date and time when the showing ends
        price: Ticket price for this showing
        showing_status: Initial status of the showing (default: "scheduled")
        current_user: The authenticated user (injected by the dependency)
        db: Database session dependency

    Returns:
        Dict: The created showing details

    Raises:
        HTTPException: If movie or room not found, or there's a scheduling conflict
    """
    # Check if user is an admin
    # TODO: validate_admin(current_user)

    # Verify that the movie exists using tmdb_id instead of id
    movie_result = await db.execute(select(Movie).filter(Movie.tmdb_id == movie_id))
    movie = movie_result.scalars().first()
    if not movie:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found")

    # Verify that the room exists
    room_result = await db.execute(select(Room).filter(Room.id == room_id))
    room = room_result.scalars().first()
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")

    # Check for time conflicts in the same room
    conflict_query = (
        select(Showing)
        .filter(Showing.room_id == room_id)
        .filter(Showing.status == "scheduled")
        .filter(
            # Check for overlapping times
            ((Showing.start_time <= start_time) & (Showing.end_time > start_time))
            | ((Showing.start_time < end_time) & (Showing.end_time >= end_time))
            | ((Showing.start_time >= start_time) & (Showing.end_time <= end_time))
        )
    )

    conflict_result = await db.execute(conflict_query)
    conflicting_showing = conflict_result.scalars().first()

    if conflicting_showing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="There is a time conflict with another showing in this room",
        )

    # Create the new showing using the movie's internal ID
    new_showing = Showing(
        movie_id=movie.id,  # Use the UUID from the movie object
        room_id=room_id,
        start_time=start_time,
        end_time=end_time,
        price=price,
        status=showing_status,
    )

    db.add(new_showing)
    await db.commit()
    await db.refresh(new_showing)

    return {
        "id": str(new_showing.id),
        "movie_id": movie_id,  # Return the TMDB ID for frontend consistency
        "room_id": str(room_id),
        "start_time": new_showing.start_time.isoformat(),
        "end_time": new_showing.end_time.isoformat(),
        "price": float(new_showing.price),
        "status": showing_status,
    }
