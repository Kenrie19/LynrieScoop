"""
User data model for the LynrieScoop cinema application.

This module defines the ORM model for users in the system, including
authentication information and role-based access control.
"""

import uuid
from datetime import datetime
from typing import Literal

from sqlalchemy import Boolean, Column, DateTime, Enum, String
from sqlalchemy.dialects.postgresql import UUID

from app.db.session import Base


class User(Base):
    """
    SQLAlchemy ORM model representing a user in the cinema system.

    This model stores user authentication details, profile information,
    and role-based access control parameters.

    Attributes:
        id (UUID): Primary key, unique identifier for the user
        email (str): User's email address (unique, used for login)
        name (str): User's display name
        hashed_password (str): Securely hashed password
        role (str): User role for access control ("user", "manager", "admin")
        is_active (bool): Whether the user account is active
        avatar (str): URL to user's avatar image
        created_at (datetime): When the user was created
        updated_at (datetime): When the user was last updated
    """

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    role: Column[Literal["user", "manager", "admin"]] = Column(
        Enum("user", "manager", "admin", name="user_role"), default="user", nullable=False
    )
    is_active = Column(Boolean, default=True)
    avatar = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
