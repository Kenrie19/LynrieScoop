"""
Database initialization module for the LynrieScoop cinema application.

This module provides functions to initialize and configure the database,
create tables from SQLAlchemy models, check the database connection,
and populate the database with seed data if needed.
"""

import logging

from sqlalchemy.sql import text

from app.db.seed_data import create_sample_data
from app.db.session import AsyncSessionLocal, Base, engine

# from app.models import (
#     Booking,
#     Movie,
#     Room,
#     SeatReservation,
#     Showing,
#     User,
# )

logger = logging.getLogger(__name__)


async def create_tables() -> None:
    """
    Create database tables from SQLAlchemy models.

    This function creates all database tables defined by SQLAlchemy models
    in the application. It uses the engine from the session module to
    establish a connection and execute DDL statements.

    Returns:
        None

    Raises:
        SQLAlchemyError: If there's an issue creating the tables
    """
    logger.info("Creating database tables...")
    async with engine.begin() as conn:
        # Drop all tables if they exist
        # await conn.run_sync(Base.metadata.drop_all)
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created successfully!")


async def check_connection() -> bool:
    """Test database connection."""
    logger.info("Testing database connection...")
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(text("SELECT 1"))
            logger.info("Database connection successful: %s", result.scalar())
            return True
    except Exception as e:
        logger.error("Database connection failed: %s", str(e))
        return False


async def init_db() -> None:
    """Initialize database."""
    connection_ok = await check_connection()
    if connection_ok:
        await create_tables()
        # Add sample data for development
        await create_sample_data()
    else:
        logger.error("Database initialization skipped due to connection failure")
