from typing import Any, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.session import get_db
from app.models.room import Room

router = APIRouter(prefix="/cinema", tags=["cinema"])


@router.get("/", response_model=dict)
async def get_cinema_info(db: AsyncSession = Depends(get_db)) -> Any:
    """
    Retrieve general information about the cinema.

    This endpoint returns basic details about the cinema including name,
    location, contact information, and a short description. This information
    is used throughout the application for display purposes.

    Args:
        db: Database session dependency (not used in this implementation)

    Returns:
        dict: Cinema information including name, address, and contact details
    """
    # Return static information about the single cinema
    return {
        "name": "Grand Cinema",
        "address": "123 Main Street",
        "city": "Movie City",
        "description": "The best cinema experience in town",
        "phone": "555-123-4567",
        "email": "info@grandcinema.com",
    }


@router.get("/rooms", response_model=List[dict])
async def get_rooms(db: AsyncSession = Depends(get_db)) -> Any:
    """
    Retrieve a list of all rooms in the cinema.

    This endpoint returns information about all available rooms in the cinema,
    including room identifiers, names, and seating capacities. This is used
    for displaying room options when browsing showings or creating screenings.

    Args:
        db: Database session dependency

    Returns:
        List[dict]: List of room objects with basic information
    """
    # Get rooms
    query = select(Room)
    result = await db.execute(query)
    rooms = result.scalars().all()

    return [{"id": str(room.id), "name": room.name, "capacity": room.capacity} for room in rooms]


@router.get("/rooms/{room_id}", response_model=dict)
async def get_room(room_id: UUID, db: AsyncSession = Depends(get_db)) -> Any:
    """
    Retrieve detailed information about a specific cinema room.

    This endpoint returns comprehensive details about a particular room in the cinema,
    including its name, seating capacity, and special features such as 3D or IMAX
    capabilities. This is used for displaying room details on booking pages.

    Args:
        room_id: UUID of the room to retrieve
        db: Database session dependency

    Returns:
        dict: Room information with complete details

    Raises:
        HTTPException: If the room with the given ID is not found
    """
    # Get room
    result = await db.execute(select(Room).filter(Room.id == room_id))
    room = result.scalars().first()

    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")

    return {
        "id": str(room.id),
        "name": room.name,
        "capacity": room.capacity,
        "has_3d": room.has_3d,
        "has_imax": room.has_imax,
        "has_dolby": room.has_dolby,
    }
