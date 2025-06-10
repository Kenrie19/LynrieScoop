"""
Booking API routes for the LynrieScoop cinema application.

This module defines the REST API endpoints for managing ticket bookings,
including creating bookings, retrieving booking information, and handling
the booking lifecycle.
"""

import json
import smtplib
import uuid
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from app.core.config import settings
from app.core.websocket_manager import get_websocket_manager
from app.core.security import get_current_user
from app.db.session import get_db
from app.models.booking import Booking
from app.models.movie import Movie
from app.models.room import Room
from app.models.seat_reservation import SeatReservation
from app.models.showing import Showing
from app.models.user import User

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

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
        select(Showing)
        .options(joinedload(Showing.room), joinedload(Showing.movie))
        .filter(Showing.id == screening_id)
    )
    screening = result.scalars().first()

    if not screening:
        raise HTTPException(status_code=404, detail="Screening not found")
    if not screening.room:
        raise HTTPException(status_code=400, detail="Room not linked to screening")

    # Fix: haal het aantal boekingen op via een aparte query
    bookings_count_result = await db.execute(
        select(func.count(Booking.id)).where(Booking.showing_id == screening_id)
    )
    bookings_count = bookings_count_result.scalar() or 0

    available_tickets = screening.room.capacity - bookings_count
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

    websocket_manager = get_websocket_manager()
    remaining = screening.room.capacity - (bookings_count + 1)  # +1 want net geboekt
    await websocket_manager.broadcast(
        f"screenings/{screening_id}/update",
        {
            "screening_id": str(screening_id),
            "available_tickets": remaining,
            "total_capacity": screening.room.capacity,
        },
    )

    message_html = (
        """<html>
        <head>
            <style>                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .header { background-color: #222; color: white; padding: 10px; text-align: center; }
                .ticket { border: 1px solid #ddd; padding: 15px; margin-top: 20px; }
                .footer { font-size: 12px; text-align: center; margin-top: 30px; color: #777; }
                .qr-code { text-align: center; margin: 20px 0; padding: 15px; background-color: #f9f9f9; }
                .qr-code img { width: 180px; height: 180px; border: 1px solid #ddd; padding: 5px; background-color: white; }
            </style>
        </head>"""
        + f"""
        <body>
            <div class="container">
                <div class="header">
                    <h1>LynrieScoop Cinema</h1>
                    <h2>Ticket Confirmation</h2>
                </div>

                <p>Dear {current_user.name},</p>

                <p>Thank you for your booking! Here are your ticket details:</p>

                <div class="ticket">
                    <p><strong>Booking Number:</strong> {booking.booking_number}</p>
                    <p>
                        <strong>Movie:</strong>
                        {screening.movie.title if screening.movie else "Unknown"}
                    </p>
                    <p><strong>Date & Time:</strong> {screening.start_time.isoformat()}</p>
                    <p><strong>Room:</strong> {screening.room.name}</p>
                    <p><strong>Total Price:</strong> ${booking.total_price}</p>
                    <p><strong>Status:</strong> {booking.status}</p>
                      <div class="qr-code">
                        <p><strong>Your Ticket QR Code:</strong></p>
                        <img src="https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={booking_id}" alt="Booking QR Code" width="180" height="180" style="width: 180px; height: 180px; display: inline-block; border: 1px solid #ddd; padding: 5px; background-color: white;" />
                        <p><small>Booking ID: {booking_id}<br>Present this QR code at the cinema entrance for quick access</small></p>
                    </div>
                </div>

                <p>Please arrive 15 minutes before the showing. Enjoy your movie!</p>

                <div class="footer">
                    <p>This is an automated message, please do not reply to this email.</p>
                    <p>&copy; 2025 LynrieScoop Cinema. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>"""
    )

    sender = f"{settings.EMAILS_FROM_NAME} <simon.stijnen@student.vives.be>"
    receiver = f"{current_user.name} <{current_user.email}>"

    if (
        not settings.SMTP_HOST
        or not settings.SMTP_PORT
        or not settings.SMTP_USER
        or not settings.SMTP_PASSWORD
    ):
        raise HTTPException(
            status_code=500,
            detail="Email settings are not configured. Please contact support.",
        )

    # Create a proper MIME email
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"LynrieScoop - Booking Confirmation - {booking.booking_number}"
    msg["From"] = sender
    msg["To"] = receiver

    # Attach HTML part
    html_part = MIMEText(message_html, "html")
    msg.attach(html_part)

    message = Mail(
        from_email="simon.stijnen@student.vives.be",
        to_emails=current_user.email,
        subject=f"LynrieScoop - Booking Confirmation - {booking.booking_number}",
        html_content=message_html,
    )

    try:
        # Initialize SendGrid client with API key
        sg = SendGridAPIClient(settings.SMTP_PASSWORD)

        # Send the email with improved error handling
        response = sg.send(message)

        if response.status_code not in [200, 201, 202]:
            # Log the error for monitoring but continue execution
            print(f"Warning: SendGrid returned status code {response.status_code}")

    except Exception as e:
        # Log the specific exception for better debugging
        print(f"SendGrid email error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to send confirmation email. Please try again later.",
        )

    # try:
    #     with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
    #         server.starttls()
    #         server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
    #         server.sendmail("simon.stijnen@student.vives.be", receiver, msg.as_string())
    #         print(f"Email sent successfully to {receiver}")
    # except Exception as e:
    #     print(f"Failed to send email: {str(e)}")
    #     # Don't raise exception here so booking can still be completed
    #     # But log the error for monitoring

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
    records. WebSocket messages are broadcast to notify other users about seat status changes.

    Args:
        reservation_data: Dictionary containing showing ID and selected seats
        db: Database session dependency
        current_user: The authenticated user (injected by the dependency)

    Returns:
        dict: Confirmation message with reservation details

    Raises:
        HTTPException: If seats are unavailable or invalid, or authentication fails
    """
    # Get WebSocket manager to broadcast seat updates
    # websocket_manager = get_websocket_manager()

    # Placeholder implementation - would need proper implementation
    # This would typically broadcast seat status changes via WebSockets
    return {"message": "Seats reserved successfully"}
