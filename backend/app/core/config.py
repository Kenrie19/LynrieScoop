import os
import secrets
from typing import List, Optional, Union

from pydantic import (
    EmailStr,
    Field,
    PostgresDsn,
    field_validator,
)
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
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
    DATABASE_URL=os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/cinema"),  # type: ignore
    JWT_SECRET=os.getenv("JWT_SECRET", "NOT_A_SECRET"),
    TMDB_API_KEY="995ebcf9d5249c3ccdbd4b689c4b5a3f",
)

print("Settings loaded:", settings.TMDB_API_KEY)  # Debugging line to check loaded settings