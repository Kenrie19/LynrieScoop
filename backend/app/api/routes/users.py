"""
User API routes for the LynrieScoop cinema application.

This module defines the REST API endpoints for user profile management,
allowing users to view and update their information.
"""

from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import User as UserSchema
from app.schemas.user import UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserSchema)
async def get_current_user_info(current_user: User = Depends(get_current_user)) -> Any:
    """
    Retrieve detailed profile information for the currently authenticated user.

    This endpoint returns the full user profile information for display in the
    user profile section of the application. It uses the authentication token
    to identify the user.

    Args:
        current_user: The authenticated user (injected by the dependency)

    Returns:
        UserSchema: Complete user profile information

    Raises:
        HTTPException: If authentication fails (handled by dependency)
    """
    return current_user


@router.put("/me", response_model=UserSchema)
async def update_current_user(
    user_update: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Update the profile information for the currently authenticated user.

    This endpoint allows users to modify their profile details such as name,
    email, or avatar. Password changes are handled through a separate endpoint.

    Args:
        user_update: Updated user information
        db: Database session dependency
        current_user: The authenticated user (injected by the dependency)

    Returns:
        UserSchema: The updated user profile information

    Raises:
        HTTPException: If authentication fails or validation errors occur
    """
    # Update user fields directly
    if user_update.name is not None:
        setattr(current_user, "name", user_update.name)
    if user_update.email is not None:
        setattr(current_user, "email", user_update.email)

    await db.commit()
    await db.refresh(current_user)

    return current_user
