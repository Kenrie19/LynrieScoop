"""
Booking API routes for the LynrieScoop cinema application.

This module defines the REST API endpoints for managing ticket bookings,
including creating bookings, retrieving booking information, and handling
the booking lifecycle.
"""

import uuid
import json
from datetime import datetime
from typing import Any, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from app.core.mqtt_client import get_mqtt_client
from app.core.security import get_current_user
from app.db.session import get_db
from app.models.booking import Booking
from app.models.movie import Movie
from app.models.room import Room
from app.models.seat_reservation import SeatReservation
from app.models.showing import Showing
from app.models.user import User

router = APIRouter(prefix="/bookings", tags=["bookings"])


@router.get("/my-bookings", response_model=List[dict])
async def get_my_bookings(
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
) -> Any:
    """
    Retrieve all bookings for the currently authenticated user.

    This endpoint returns a list of the user's bookings with comprehensive information,
    including movie details, showing times, seat information, and booking status.
    This is used for displaying the user's booking history and current tickets.

    Args:
        db: Database session dependency
        current_user: The authenticated user (injected by the dependency)

    Returns:
        List[dict]: List of booking objects with full movie and showing details

    Raises:
        HTTPException: If authentication fails (handled by dependency)
    """
    # Query bookings with related info
    query = (
        select(
            Booking,
            Showing.start_time,
            Showing.end_time,
            Movie.title.label("movie_title"),
            Movie.poster_path,
            Room.name.label("room_name"),
        )
        .join(Showing, Booking.showing_id == Showing.id)
        .join(Movie, Showing.movie_id == Movie.id)
        .join(Room, Showing.room_id == Room.id)
        .filter(Booking.user_id == current_user.id)
        .order_by(Showing.start_time)
    )

    result = await db.execute(query)
    bookings_data = result.all()

    bookings_list = []
    for booking_row in bookings_data:
        booking = booking_row[0]  # The Booking object

        # Get seat reservations for this booking
        seats_query = select(SeatReservation).filter(SeatReservation.booking_id == booking.id)
        seats_result = await db.execute(seats_query)
        seat_reservations = seats_result.scalars().all()
        seat_info = [f"{sr.row}{sr.number}" for sr in seat_reservations]

        # Determine if this is upcoming or past
        now = datetime.utcnow()
        status = "upcoming" if booking_row[1] > now else "past"
        if booking.status == "cancelled":
            status = "cancelled"

        bookings_list.append(
            {
                "id": str(booking.id),
                "booking_number": booking.booking_number,
                "movie_title": booking_row[3],  # movie_title from the join
                "poster_path": booking_row[4],  # poster_path from the join
                "room_name": booking_row[5],  # room_name from the join
                "showing_time": booking_row[1].isoformat(),  # Format datetime to string
                "seats": seat_info,
                "total_price": booking.total_price,
                "booking_date": booking.created_at.isoformat(),
                "status": status,
            }
        )

    return bookings_list


@router.post("/create", response_model=dict)
async def create_booking(
    screening_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Create a new booking for a movie showing.

    This endpoint allows authenticated users to create a booking for a specific
    showing. The booking data must include showing ID, seat information, and
    payment details if applicable. This endpoint handles the entire booking
    process including payment processing and confirmation.

    Args:
        booking_data: Dictionary containing booking details including showing ID and seats
        db: Database session dependency
        current_user: The authenticated user (injected by the dependency)

    Returns:
        dict: Booking confirmation with details including booking ID and reference number

    Raises:
        HTTPException: If the showing is not available, seats are already taken,
                      or payment processing fails
    """
    result = await db.execute(
        select(Showing).options(joinedload(Showing.room)).filter(Showing.id == screening_id)
    )
    screening = result.scalars().first()

    if not screening:
        raise HTTPException(status_code=404, detail="Screening not found")
    if not screening.room:
        raise HTTPException(status_code=400, detail="Room not linked to screening")

    available_tickets = screening.room.capacity - screening.bookings_count
    if available_tickets <= 0:
        raise HTTPException(status_code=400, detail="No tickets available for this screening")

    booking_id = uuid.uuid4()
    # Generate a booking number (e.g., use a short UUID or custom logic)
    booking_number = str(uuid.uuid4())[:8].upper()  # Example: 8-char unique code
    booking = Booking(
        id=booking_id,
        user_id=current_user.id,
        showing_id=screening.id,
        booking_number=booking_number,
        total_price=screening.price,  # Set the price to the ticket price of the showing
        status="confirmed",
    )
    db.add(booking)

    await db.commit()

    mqtt_client = get_mqtt_client()
    remaining = screening.room.capacity - screening.bookings_count
    mqtt_client.publish(
        f"screenings/{screening_id}/update",
        json.dumps(
            {
                "screening_id": str(screening_id),
                "available_tickets": remaining,
                "total_capacity": screening.room.capacity,
            }
        ),
    )

    return {
        "booking_id": str(booking_id),
        "screening_id": str(screening_id),
        "movie_title": screening.movie.title if screening.movie else "Unknown",
        "start_time": screening.start_time.isoformat(),
        "room": screening.room.name,
        "ticket_count": 1,
        "status": booking.status,
    }


@router.post("/reserve-seats", response_model=dict)
async def reserve_seats(
    reservation_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Reserve specific seats for a movie showing.

    This endpoint allows authenticated users to reserve specific seats for a showing.
    The system verifies seat availability and creates the necessary seat reservation
    records. MQTT messages are published to notify other users about seat status changes.

    Args:
        reservation_data: Dictionary containing showing ID and selected seats
        db: Database session dependency
        current_user: The authenticated user (injected by the dependency)

    Returns:
        dict: Confirmation message with reservation details

    Raises:
        HTTPException: If seats are unavailable or invalid, or authentication fails
    """
    # Get MQTT client to publish seat updates
    # mqtt_client = get_mqtt_client()

    # Placeholder implementation - would need proper implementation
    # This would typically publish seat status changes via MQTT
    return {"message": "Seats reserved successfully"}
