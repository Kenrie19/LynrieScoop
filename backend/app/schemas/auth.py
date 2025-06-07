"""
Authentication schema definitions for the LynrieScoop cinema application.

This module provides Pydantic models for authentication data validation,
serialization, and documentation in the API, including models for tokens,
login requests, and user registration.
"""

from typing import Optional

from pydantic import BaseModel


class Token(BaseModel):
    """
    Schema for authentication token response.

    This model represents the token returned after successful authentication,
    following the OAuth2 bearer token specification.

    Attributes:
        access_token (str): JWT access token for authentication
        token_type (str): Type of token, always "bearer" in this application
    """

    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """
    Schema for JWT token payload content.

    Represents the data encoded in JWT tokens used for authentication.

    Attributes:
        sub (str, optional): Subject of the token (usually user ID)
        exp (int, optional): Expiration timestamp of the token
        role (str, optional): User role for authorization checks
    """

    sub: Optional[str] = None
    exp: Optional[int] = None
    role: Optional[str] = None


class LoginRequest(BaseModel):
    """
    Schema for user login request.

    Defines the data structure for login API endpoint requests.

    Attributes:
        email (str): User's email address
        password (str): User's password (plain text for request only)
    """

    email: str
    password: str


class RegisterRequest(BaseModel):
    """
    Schema for user registration request.

    Defines the data structure for user registration API endpoint requests.

    Attributes:
        name (str): User's full name
        email (str): User's email address
        password (str): User's chosen password (plain text for request only)
    """

    name: str
    email: str
    password: str
