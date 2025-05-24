"""
User schema definitions for the LynrieScoop cinema application.

This module provides Pydantic models for user data validation,
serialization, and documentation in the API, including models for
user creation, updates, and responses.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """
    Base user schema with common attributes shared across user models.

    Attributes:
        email: User's email address (validated as proper email format)
        name: User's full name
        is_active: Whether the user account is active (default: True)
    """

    email: EmailStr
    name: str
    is_active: bool = True


class UserCreate(UserBase):
    """
    Schema for creating a new user.

    Extends the base user schema with password requirements.

    Attributes:
        password: User's password (minimum 8 characters)
    """

    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    """
    Schema for updating an existing user profile.

    All fields are optional, allowing partial updates.

    Attributes:
        email: Optional new email address
        name: Optional new name
        password: Optional new password
        avatar: Optional URL to user's profile image
    """

    email: Optional[EmailStr] = None
    name: Optional[str] = None
    password: Optional[str] = None
    avatar: Optional[str] = None


class UserInDBBase(UserBase):
    """
    Base schema for user data retrieved from the database.

    Extends the base user schema with system-generated attributes.

    Attributes:
        id: Unique identifier for the user (UUID)
        role: User's role (e.g., "user", "manager", "admin")
        created_at: Timestamp of when the user account was created
        avatar: Optional URL to user's profile image
    """

    id: UUID
    role: str
    created_at: datetime
    avatar: Optional[str] = None

    class Config:
        from_attributes = True


class User(UserInDBBase):
    """
    Complete user data schema returned to API clients.

    This schema is used for responses when retrieving user information.
    It includes all user attributes except password-related fields.
    """


class UserInDB(UserInDBBase):
    """
    Complete user data schema as stored in the database.

    This internal schema includes the hashed password field that should
    never be exposed to API clients.

    Attributes:
        hashed_password: Securely hashed version of the user's password
    """

    hashed_password: str
