"""
Configuration settings for the LynrieScoop cinema application.

This module defines application settings using Pydantic BaseSettings,
which allows for environment variable validation, typing, and defaults.
"""

import os
import secrets
from typing import List, Optional, Union

from dotenv import load_dotenv
from pydantic import EmailStr, Field, PostgresDsn, field_validator
from pydantic_settings import BaseSettings

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    """
    Application settings with environment variable loading and validation.

    This class defines all configuration parameters for the application,
    with defaults that can be overridden by environment variables.

    Attributes:
        API_V1_STR: API version prefix for URL paths
        SECRET_KEY: Secret key for JWT token signing
        ACCESS_TOKEN_EXPIRE_MINUTES: JWT token expiration time
        CORS_ORIGINS: List of allowed origins for CORS
        ALLOWED_HOSTS: List of allowed hosts for trusted host middleware
        DATABASE_URL: PostgreSQL database connection string
        MQTT_BROKER: Hostname or IP of the MQTT broker
        MQTT_PORT: Port for the MQTT broker connection
        TMDB_API_KEY: API key for The Movie Database API
        TMDB_API_BASE_URL: Base URL for TMDB API requests
    """

    # API configuration
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days

    # CORS configuration
    CORS_ORIGINS: List[str] = Field(default_factory=list)
    ALLOWED_HOSTS: List[str] = Field(default_factory=list)

    # Database configuration
    DATABASE_URL: Optional[PostgresDsn] = Field(None)

    # MQTT configuration
    MQTT_BROKER: str = "localhost"
    MQTT_PORT: int = 1883

    # TMDB configuration
    TMDB_API_KEY: str = Field("NOT_A_SECRET")
    TMDB_API_BASE_URL: str = "https://api.themoviedb.org/3"

    # Environment
    ENVIRONMENT: str = "dev"

    # JWT configuration
    JWT_SECRET: str = Field("NOT_A_SECRET")
    JWT_ALGORITHM: str = "HS256"

    # Email settings for future use
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[EmailStr] = None
    EMAILS_FROM_NAME: Optional[str] = None

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        if isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    @field_validator("ALLOWED_HOSTS", mode="before")
    @classmethod
    def assemble_allowed_hosts(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            return [host.strip() for host in v.split(",")]
        return v or ["localhost", "127.0.0.1"]

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings(
    DATABASE_URL=os.getenv(
        "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/cinema"  # type: ignore
    ),
    JWT_SECRET=os.getenv("JWT_SECRET", "NOT_A_SECRET"),
    TMDB_API_KEY=os.getenv("TMDB_API_KEY", "NOT_A_SECRET"),
    SMTP_HOST=os.getenv("SMTP_HOST"),
    SMTP_PORT=int(os.getenv("SMTP_PORT", "587")),
    SMTP_USER=os.getenv("SMTP_USER"),
    SMTP_PASSWORD=os.getenv("SMTP_PASSWORD"),
    EMAILS_FROM_EMAIL=os.getenv("EMAILS_FROM_EMAIL", "simon.stijnen@student.vives.be"),
    EMAILS_FROM_NAME=os.getenv("EMAILS_FROM_NAME", "LynrieScoop"),
)
