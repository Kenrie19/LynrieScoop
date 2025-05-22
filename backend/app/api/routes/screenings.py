from typing import Any, List, Optional, Dict
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status, Body, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from app.core.security import get_current_user, get_current_manager_user
from app.db.session import get_db
from app.models.showing import Showing
from app.models.room import Room
from app.models.movie import Movie
from app.models.user import User
from app.core.config import settings

import tmdbsimple as tmdb

tmdb.API_KEY = settings.TMDB_API_KEY

router = APIRouter(prefix="/screenings", tags=["screenings"])


@router.get("/", response_model=List[Dict])
async def get_screenings(
    movie_id: int = Query(..., description="TMDB ID of the movie"),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get all planned screenings
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
    screenings_list = [
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

    return screenings_list


@router.get("/{id}/tickets", response_model=Dict)
async def get_screening_tickets(
    id: UUID,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get available tickets for a specific screening
    """
    result = await db.execute(
        select(Showing).options(joinedload(Showing.room)).filter(Showing.id == id)
    )
    showing = result.scalars().first()

    if not showing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Screening not found")

    available_tickets = showing.room.capacity - showing.bookings_count if showing.room else 0

    return {
        "screening_id": str(showing.id),
        "total_capacity": showing.room.capacity if showing.room else 0,
        "available_tickets": available_tickets,
        "price": showing.price,
    }


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_screening(
    movie_id: int = Body(..., description="TMDB Movie ID"),
    room_id: UUID = Body(..., description="Room ID"),
    start_time: datetime = Body(..., description="Start time of the screening"),
    end_time: datetime = Body(..., description="End time of the screening"),
    price: float = Body(..., description="Ticket price"),
    current_user: User = Depends(get_current_manager_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Create a new screening for a movie
    Only managers can create screenings
    """
    # Check if user is a manager
    if current_user.role != "manager":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

    # Verify that the movie exists using tmdb_id
    movie_result = await db.execute(select(Movie).filter(Movie.tmdb_id == movie_id))
    movie = movie_result.scalars().first()
    print(f"DEBUG: Searching movie with tmdb_id={movie_id}")

    # If movie doesn't exist in our database, create it using TMDB data
    if not movie:
        try:
            print("DEBUG: Movie not found locally, trying TMDB...")
            collection = tmdb.Movies(movie_id)
            tmdb_movie = collection.info()

            movie = Movie(
                tmdb_id=movie_id,
                title=tmdb_movie.get("title", "Unknown"),
                overview=tmdb_movie.get("overview", ""),
                poster_path=tmdb_movie.get("poster_path", ""),
                release_date=tmdb_movie.get("release_date"),
            )
            db.add(movie)
            await db.flush()  # Get the ID without committing transaction
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found in TMDB"
            )

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
            detail="There is a time conflict with another screening in this room",
        )

    # Create the new screening
    new_screening = Showing(
        movie_id=movie.id,
        room_id=room_id,
        start_time=start_time,
        end_time=end_time,
        price=price,
        status="scheduled",
        bookings_count=0,
    )

    db.add(new_screening)
    await db.commit()
    await db.refresh(new_screening)

    return {
        "id": str(new_screening.id),
        "movie_id": movie_id,
        "room_id": str(room_id),
        "start_time": new_screening.start_time.isoformat(),
        "end_time": new_screening.end_time.isoformat(),
        "price": new_screening.price,
        "status": new_screening.status,
    }


@router.put("/{id}", status_code=status.HTTP_200_OK)
async def update_screening(
    id: UUID,
    room_id: Optional[UUID] = Body(None, description="Room ID"),
    start_time: Optional[datetime] = Body(None, description="Start time of the screening"),
    end_time: Optional[datetime] = Body(None, description="End time of the screening"),
    price: Optional[float] = Body(None, description="Ticket price"),
    status: Optional[str] = Body(None, description="Status of the screening"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Update a screening
    Only managers can update screenings
    """
    # Check if user is a manager
    if current_user.role != "manager":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

    # Verify that the screening exists
    result = await db.execute(select(Showing).filter(Showing.id == id))
    screening = result.scalars().first()

    if not screening:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Screening not found")

    # Update fields if provided
    if room_id is not None:
        # Verify that the room exists
        room_result = await db.execute(select(Room).filter(Room.id == room_id))
        room = room_result.scalars().first()
        if not room:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")
        screening.room_id = room_id

    if start_time is not None:
        screening.start_time = start_time

    if end_time is not None:
        screening.end_time = end_time

    if price is not None:
        screening.price = price

    if status is not None:
        screening.status = status

    # Check for time conflicts if room or times were updated
    if room_id is not None or start_time is not None or end_time is not None:
        actual_start = start_time if start_time is not None else screening.start_time
        actual_end = end_time if end_time is not None else screening.end_time
        actual_room = room_id if room_id is not None else screening.room_id

        conflict_query = (
            select(Showing)
            .filter(Showing.room_id == actual_room)
            .filter(Showing.status == "scheduled")
            .filter(Showing.id != id)  # Exclude the current screening
            .filter(
                # Check for overlapping times
                ((Showing.start_time <= actual_start) & (Showing.end_time > actual_start))
                | ((Showing.start_time < actual_end) & (Showing.end_time >= actual_end))
                | ((Showing.start_time >= actual_start) & (Showing.end_time <= actual_end))
            )
        )

        conflict_result = await db.execute(conflict_query)
        conflicting_showing = conflict_result.scalars().first()

        if conflicting_showing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="There is a time conflict with another screening in this room",
            )

    await db.commit()
    await db.refresh(screening)

    # Get movie details for response
    movie_result = await db.execute(select(Movie).filter(Movie.id == screening.movie_id))
    movie = movie_result.scalars().first()
    movie_id = movie.tmdb_id if movie else None

    return {
        "id": str(screening.id),
        "movie_id": movie_id,
        "room_id": str(screening.room_id),
        "start_time": screening.start_time.isoformat(),
        "end_time": screening.end_time.isoformat() if screening.end_time else None,
        "price": screening.price,
        "status": screening.status,
    }


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_screening(
    id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """
    Delete a screening
    Only managers can delete screenings
    """
    # Check if user is a manager
    if current_user.role != "manager":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

    # Verify that the screening exists
    result = await db.execute(select(Showing).filter(Showing.id == id))
    screening = result.scalars().first()

    if not screening:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Screening not found")

    # Delete the screening
    await db.delete(screening)
    await db.commit()

    # For a 204 response, don't return anything
