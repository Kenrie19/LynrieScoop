"""
Booking data model for the LynrieScoop cinema application.

This module defines the ORM model for customer bookings, representing
ticket reservations for movie showings with payment and status tracking.
"""

import uuid
from datetime import datetime
from typing import Literal

from sqlalchemy import Column, DateTime, Enum, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.session import Base


class Booking(Base):
    """
    SQLAlchemy ORM model representing a customer booking in the cinema system.

    This model stores comprehensive information about customer ticket bookings,
    including references to the customer, showing, payment details, and
    the current status of the booking in its lifecycle.

    Attributes:
        id (UUID): Primary key, unique identifier for the booking
        user_id (UUID): Foreign key to the users table
        showing_id (UUID): Foreign key to the showings table
        booking_number (str): Unique booking reference number for customers
        total_price (float): Total price of the booking
        status (str): Current status of the booking:
            - "pending": Initial state when booking is created
            - "confirmed": Booking confirmed after payment
            - "cancelled": Booking cancelled by customer or system
            - "completed": Booking completed after movie showing
        payment_method (str): Method of payment (e.g., "credit_card", "paypal")
        payment_id (str): External payment reference ID
        created_at (datetime): When the booking was created
        updated_at (datetime): When the booking was last updated

    Relationships:
        seat_reservations: Associated seat reservations for this booking
        user: The user who made this booking
        showing: The movie showing this booking is for
    """

    __tablename__ = "bookings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    showing_id = Column(UUID(as_uuid=True), ForeignKey("showings.id"), nullable=False)
    booking_number = Column(String, unique=True, nullable=False, index=True)
    total_price = Column(Float, nullable=False)
    status: Column[Literal["pending", "confirmed", "cancelled", "completed"]] = Column(
        Enum("pending", "confirmed", "cancelled", "completed", name="booking_status"),
        default="pending",
        nullable=False,
    )
    payment_method = Column(String, nullable=True)
    payment_id = Column(String, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", backref="bookings")
    showing = relationship("Showing", back_populates="bookings")
    seat_reservations = relationship(
        "SeatReservation", back_populates="booking", cascade="all, delete-orphan"
    )
