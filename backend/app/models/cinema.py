"""
Cinema data model for the LynrieScoop cinema application.

This module defines the ORM model for cinemas/theaters, representing
physical locations where movies are screened.
"""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.session import Base


class Cinema(Base):
    """
    SQLAlchemy ORM model representing a cinema/theater in the system.

    This model stores information about the physical cinema locations,
    including contact details, address information, and related screening rooms.

    Attributes:
        id (UUID): Primary key, unique identifier for the cinema
        name (str): Name of the cinema
        address (str): Street address of the cinema
        city (str): City where the cinema is located
        state (str, optional): State/province where the cinema is located
        postal_code (str, optional): Postal/ZIP code of the cinema
        phone (str, optional): Contact phone number
        email (str, optional): Contact email address
        description (Text, optional): Detailed description of the cinema
        image_url (str, optional): URL to an image of the cinema
        is_active (bool): Whether the cinema is currently active
        created_at (datetime): When the cinema record was created
        updated_at (datetime): When the cinema record was last updated

    Relationships:
        rooms: The screening rooms within this cinema
    """

    __tablename__ = "cinemas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False, index=True)
    address = Column(String, nullable=False)
    city = Column(String, nullable=False, index=True)
    state = Column(String, nullable=True)
    postal_code = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    image_url = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    rooms = relationship("Room", back_populates="cinema", cascade="all, delete-orphan")
