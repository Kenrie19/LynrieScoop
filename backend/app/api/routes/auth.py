"""
Authentication API routes for the LynrieScoop cinema application.

This module defines REST API endpoints for user authentication,
including login, registration, and token management.
"""

from datetime import timedelta
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.config import settings
from app.core.security import (
    create_access_token,
    get_current_user,
    get_password_hash,
    verify_password,
)
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest, Token

router = APIRouter(tags=["auth"])


@router.post("/login", response_model=Token)
async def login(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Authenticate a user and return a JWT token.

    This endpoint validates user credentials and issues a JWT access token
    for authenticated API access.

    Args:
        login_data: Email and password credentials
        db: Database session dependency

    Returns:
        Token: Object containing access token and token type

    Raises:
        HTTPException: If credentials are invalid or user not found
    """
    # Find the user by email
    result = await db.execute(select(User).filter(User.email == login_data.email))
    user = result.scalars().first()  # Validate credentials
    if not user or not verify_password(login_data.password, str(user.hashed_password)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if user is active
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")

    # Create access token with role information
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role},
        expires_delta=access_token_expires,
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=Token)
async def register(
    register_data: RegisterRequest,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Register a new user account and return a JWT token.

    This endpoint creates a new user account with the provided information,
    hashes the password for secure storage, and returns an access token
    for immediate authentication after registration.

    Args:
        register_data: User registration information including name, email and password
        db: Database session dependency

    Returns:
        Token: Object containing access token and token type for the new user

    Raises:
        HTTPException: If a user with the provided email already exists
    """
    # Check if user with this email already exists
    result = await db.execute(select(User).filter(User.email == register_data.email))
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )

    # Create new user with 'user' role by default
    hashed_password = get_password_hash(register_data.password)
    new_user = User(
        email=register_data.email,
        name=register_data.name,
        hashed_password=hashed_password,
        role="user",  # Default role is user
        is_active=True,
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    # Create and return access token for the new user
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(new_user.id), "role": new_user.role},
        expires_delta=access_token_expires,
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=Dict)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Retrieve information about the currently authenticated user.

    This endpoint returns basic profile information about the authenticated user
    based on their JWT token. This is used for profile displays and
    authorization checks in the frontend.

    Args:
        current_user: The authenticated user (injected by the dependency)

    Returns:
        Dict: Object containing user ID, email, name, and role

    Raises:
        HTTPException: If no valid token is provided (handled by dependency)
    """
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "name": current_user.name,
        "role": current_user.role,
    }
