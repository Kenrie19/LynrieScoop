# from app.core.mqtt_client import publish_screening_update
import uuid
from typing import Any, Dict
from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.booking import Booking
from app.models.showing import Showing
from app.models.user import User

router = APIRouter(tags=["reserve"])


@router.post("/reserve", status_code=status.HTTP_201_CREATED, response_model=Dict)
async def reserve_ticket(
    screening_id: UUID = Body(..., description="The ID of the screening to reserve a ticket for"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Reserve a ticket for a specific movie screening.

    This endpoint allows authenticated users to reserve a single ticket for a
    movie screening. The system verifies ticket availability before creating the
    booking and updates the screening's remaining ticket count.

    Args:
        screening_id: UUID of the screening to reserve a ticket for
        current_user: The authenticated user (injected by the dependency)
        db: Database session dependency

    Returns:
        Dict: Booking confirmation with details including booking ID and status

    Raises:
        HTTPException: If screening not found or no tickets are available
    """
    # Get the screening
    result = await db.execute(
        select(Showing).options(joinedload(Showing.room)).filter(Showing.id == screening_id)
    )
    screening = result.scalars().first()

    if not screening:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Screening not found")

    # Check if there are available tickets
    if screening.bookings_count >= screening.room.capacity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No tickets available for this screening",
        )

    # Create a new booking
    booking = Booking(
        id=uuid.uuid4(),
        user_id=current_user.id,
        showing_id=screening_id,
        booking_time=screening.start_time,
        status="confirmed",
        ticket_count=1,  # Each user can only book 1 ticket at a time
    )

    db.add(booking)

    # Update the screening booking count
    screening.bookings_count += 1

    await db.commit()

    # Publish update to all clients via MQTT
    # remaining_tickets = screening.room.capacity - screening.bookings_count
    # await publish_screening_update(
    #     str(screening_id),
    #     {
    #         "id": str(screening_id),
    #         "available_tickets": remaining_tickets,
    #         "total_capacity": screening.room.capacity,
    #     },
    # )

    return {
        "booking_id": str(booking.id),
        "screening_id": str(screening_id),
        "movie_title": screening.movie.title if screening.movie else "Unknown",
        "start_time": screening.start_time.isoformat(),
        "room": screening.room.name if screening.room else "Unknown",
        "ticket_count": 1,
        "status": booking.status,
    }
