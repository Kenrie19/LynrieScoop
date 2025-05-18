from datetime import datetime
from typing import Any, List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

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
    Get current user's bookings with complete information including movie and showing details
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
    booking_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Create a new booking
    """
    # Placeholder implementation - would need proper implementation with MQTT integration
    return {"message": "Booking created successfully"}


@router.post("/reserve-seats", response_model=dict)
async def reserve_seats(
    reservation_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Reserve seats for a showing
    """
    # Get MQTT client to publish seat updates
    # mqtt_client = get_mqtt_client()

    # Placeholder implementation - would need proper implementation
    # This would typically publish seat status changes via MQTT
    return {"message": "Seats reserved successfully"}
