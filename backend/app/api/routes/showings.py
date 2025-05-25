from typing import Any, List, Optional, Dict
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from app.core.security import get_current_user, get_current_manager_user
from app.db.session import get_db
from app.models.showing import Showing
from app.models.room import Room
from app.models.movie import Movie
from app.models.user import User

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
        .join(Room)
        .filter(Showing.movie_id == movie.id)
        .filter(Showing.status == "scheduled")
    )
    showings = result.all()

    return [
        {
            "id": str(s.id),
            "movie_id": movie_id,
            "room_id": str(r.id),
            "room_name": r.name,
            "start_time": s.start_time.isoformat(),
            "end_time": s.end_time.isoformat() if s.end_time else None,
            "price": s.price,
        }
        for s, r in showings
    ]


@router.get("/{id}/tickets", response_model=Dict)
async def get_showing_tickets(
    id: UUID,
    db: AsyncSession = Depends(get_db),
) -> Any:
    result = await db.execute(
        select(Showing).options(joinedload(Showing.room)).filter(Showing.id == id)
    )
    showing = result.scalars().first()
    if not showing:
        raise HTTPException(status_code=404, detail="Showing not found")

    return {
        "showing_id": str(showing.id),
        "total_capacity": showing.room.capacity,
        "available_tickets": showing.room.capacity - showing.bookings_count,
        "price": showing.price,
    }


@router.get("/{id}/seats", response_model=List[Dict])
async def get_showing_seats(
    id: UUID,
    db: AsyncSession = Depends(get_db),
) -> Any:
    result = await db.execute(select(Showing).options(joinedload(Showing.room)).filter(Showing.id == id))
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
            seats.append({
                "id": f"{row}{number}",
                "row": row,
                "number": number,
                "status": status,
                "isAccessible": is_accessible,
                "price": 15.0 if is_accessible else 12.0,
            })

    return seats


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_showing(
    movie_id: int = Body(...),
    room_id: UUID = Body(...),
    start_time: datetime = Body(...),
    end_time: datetime = Body(...),
    price: float = Body(...),
    current_user: User = Depends(get_current_manager_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    result = await db.execute(select(Movie).filter(Movie.tmdb_id == movie_id))
    movie = result.scalars().first()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    result = await db.execute(select(Room).filter(Room.id == room_id))
    room = result.scalars().first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    conflict_query = (
        select(Showing)
        .filter(Showing.room_id == room_id)
        .filter(Showing.status == "scheduled")
        .filter(
            ((Showing.start_time <= start_time) & (Showing.end_time > start_time))
            | ((Showing.start_time < end_time) & (Showing.end_time >= end_time))
            | ((Showing.start_time >= start_time) & (Showing.end_time <= end_time))
        )
    )
    conflict = (await db.execute(conflict_query)).scalars().first()
    if conflict:
        raise HTTPException(status_code=400, detail="Time conflict in room")

    new_showing = Showing(
        movie_id=movie.id,
        room_id=room_id,
        start_time=start_time,
        end_time=end_time,
        price=price,
        status="scheduled",
        bookings_count=0,
    )
    db.add(new_showing)
    await db.commit()
    await db.refresh(new_showing)

    return {
        "id": str(new_showing.id),
        "movie_id": movie_id,
        "room_id": str(room_id),
        "start_time": new_showing.start_time.isoformat(),
        "end_time": new_showing.end_time.isoformat(),
        "price": new_showing.price,
        "status": new_showing.status,
    }


@router.put("/{id}", status_code=status.HTTP_200_OK)
async def update_showing(
    id: UUID,
    room_id: Optional[UUID] = Body(None),
    start_time: Optional[datetime] = Body(None),
    end_time: Optional[datetime] = Body(None),
    price: Optional[float] = Body(None),
    status: Optional[str] = Body(None),
    current_user: User = Depends(get_current_manager_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    result = await db.execute(select(Showing).filter(Showing.id == id))
    showing = result.scalars().first()
    if not showing:
        raise HTTPException(status_code=404, detail="Showing not found")

    if room_id:
        room = (await db.execute(select(Room).filter(Room.id == room_id))).scalars().first()
        if not room:
            raise HTTPException(status_code=404, detail="Room not found")
        showing.room_id = room_id

    if start_time:
        showing.start_time = start_time
    if end_time:
        showing.end_time = end_time
    if price:
        showing.price = price
    if status:
        showing.status = status

    if room_id or start_time or end_time:
        actual_room = room_id or showing.room_id
        actual_start = start_time or showing.start_time
        actual_end = end_time or showing.end_time

        conflict_query = (
            select(Showing)
            .filter(Showing.room_id == actual_room)
            .filter(Showing.status == "scheduled")
            .filter(Showing.id != id)
            .filter(
                ((Showing.start_time <= actual_start) & (Showing.end_time > actual_start))
                | ((Showing.start_time < actual_end) & (Showing.end_time >= actual_end))
                | ((Showing.start_time >= actual_start) & (Showing.end_time <= actual_end))
            )
        )
        conflict = (await db.execute(conflict_query)).scalars().first()
        if conflict:
            raise HTTPException(status_code=400, detail="Time conflict in room")

    await db.commit()
    await db.refresh(showing)

    movie = (await db.execute(select(Movie).filter(Movie.id == showing.movie_id))).scalars().first()

    return {
        "id": str(showing.id),
        "movie_id": movie.tmdb_id if movie else None,
        "room_id": str(showing.room_id),
        "start_time": showing.start_time.isoformat(),
        "end_time": showing.end_time.isoformat() if showing.end_time else None,
        "price": showing.price,
        "status": showing.status,
    }


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_showing(
    id: UUID,
    current_user: User = Depends(get_current_manager_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    result = await db.execute(select(Showing).filter(Showing.id == id))
    showing = result.scalars().first()
    if not showing:
        raise HTTPException(status_code=404, detail="Showing not found")

    await db.delete(showing)
    await db.commit()
