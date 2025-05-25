from typing import Any, Dict, List, Optional
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.showing import Showing
from app.models.user import User
from app.models.booking import Booking
from app.models.seat_reservation import SeatReservation
from app.core.mqtt_client import get_mqtt_client

import uuid

router = APIRouter(prefix="/reserve", tags=["reserve"])


@router.post("/reserve", status_code=status.HTTP_201_CREATED, response_model=Dict)
async def reserve_ticket(
    screening_id: UUID = Body(..., description="The ID of the screening to reserve a ticket for"),
    seats: Optional[List[str]] = Body(None, description="List of seat identifiers (e.g. A1, B5)"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Reserve a ticket for a screening (optionally with specific seats).
    """
    # Get the screening
    result = await db.execute(
        select(Showing)
        .options(joinedload(Showing.room))
        .filter(Showing.id == screening_id)
    )
    screening = result.scalars().first()

    if not screening:
        raise HTTPException(status_code=404, detail="Screening not found")

    if not screening.room:
        raise HTTPException(status_code=400, detail="Room not linked to screening")

    # Check if tickets are available
    available_tickets = screening.room.capacity - screening.bookings_count
    if available_tickets <= 0:
        raise HTTPException(status_code=400, detail="No tickets available for this screening")

    # Check if enough seats are requested
    if seats and len(seats) > available_tickets:
        raise HTTPException(status_code=400, detail="Not enough tickets available for selected seats")

    # Create booking
    booking_id = uuid.uuid4()
    booking = Booking(
        id=booking_id,
        user_id=current_user.id,
        showing_id=screening.id,
        status="confirmed",
    )
    db.add(booking)

    # Add seat reservations if provided
    if seats:
        for seat in seats:
            row = seat[0].upper()
            try:
                number = int(seat[1:])
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid seat format: {seat}")
            db.add(SeatReservation(booking_id=booking_id, row=row, number=number))

    # Update bookings count
    screening.bookings_count += len(seats) if seats else 1
    await db.commit()

    # Optional: publish MQTT update
    mqtt_client = get_mqtt_client()
    remaining = screening.room.capacity - screening.bookings_count
    mqtt_client.publish(
        f"screenings/{screening_id}/update",
        {
            "screening_id": str(screening_id),
            "available_tickets": remaining,
            "total_capacity": screening.room.capacity,
        }
    )

    return {
        "booking_id": str(booking_id),
        "screening_id": str(screening_id),
        "movie_title": screening.movie.title if screening.movie else "Unknown",
        "start_time": screening.start_time.isoformat(),
        "room": screening.room.name,
        "ticket_count": len(seats) if seats else 1,
        "status": booking.status,
        "seats": seats or ["auto-assigned"]
    }

@router.get("/my-bookings", response_model=List[Dict])
async def get_my_bookings(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Get all bookings made by the current user.
    """
    result = await db.execute(
        select(Booking)
        .filter(Booking.user_id == current_user.id)
        .order_by(Booking.booking_time.desc())
    )
    bookings = result.scalars().all()

    if not bookings:
        return []

    bookings_list = []
    for booking in bookings:
        seats_query = select(SeatReservation).filter(SeatReservation.booking_id == booking.id)
        seats_result = await db.execute(seats_query)
        seat_reservations = seats_result.scalars().all()
        seat_info = [f"{sr.row}{sr.number}" for sr in seat_reservations]

        bookings_list.append({
            "id": str(booking.id),
            "booking_number": booking.booking_number,
            "movie_title": booking.showing.movie.title if booking.showing and booking.showing.movie else "Unknown",
            "showing_time": booking.showing.start_time.isoformat() if booking.showing else None,
            "room_name": booking.showing.room.name if booking.showing and booking.showing.room else "Unknown",
            "seats": seat_info,
            "total_price": booking.total_price,
            "booking_date": booking.created_at.isoformat(),
            "status": booking.status,
        })

    return bookings_list

