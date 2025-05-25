import asyncio
import logging
import random
from datetime import datetime, timedelta

from sqlalchemy.sql import text

from app.core.security import get_password_hash
from app.db.session import AsyncSessionLocal
from app.models.cinema import Cinema
from app.models.movie import Movie
from app.models.room import Room
from app.models.seat import Seat
from app.models.showing import Showing
from app.models.user import User

logger = logging.getLogger(__name__)


async def create_sample_data() -> None:
    """Create sample data for development and testing."""
    logger.info("Creating sample data...")

    async with AsyncSessionLocal() as session:
        # Check if we already have users
        result = await session.execute(text("SELECT COUNT(*) FROM users"))
        user_count = result.scalar()

        if user_count is not None and user_count > 0:
            logger.info("Sample data already exists, skipping...")
            return

        # Create admin user
        admin_user = User(
            email="admin@cinema.com",
            hashed_password=get_password_hash("admin"),
            role="admin",
            name="Admin User",
        )
        session.add(admin_user)

        # Create regular user
        regular_user = User(
            email="user@cinema.com",
            hashed_password=get_password_hash("password"),
            role="user",
            name="Regular User",
        )
        session.add(regular_user)

        # Create a cinema
        cinema = Cinema(
            name="Central Cinema",
            address="123 Main Street",
            city="New York",
            state="NY",
            postal_code="10001",
            phone="555-123-4567",
            email="info@centralcinema.com",
            description="A premier cinema experience in the heart of the city",
        )
        session.add(cinema)

        # Commit to get cinema ID
        await session.commit()

        # Create rooms in the cinema
        room1 = Room(name="Room 1", capacity=50, has_3d=True, cinema_id=cinema.id)
        session.add(room1)

        room2 = Room(name="Room 2", capacity=80, has_imax=True, cinema_id=cinema.id)
        session.add(room2)

        # Commit to get IDs
        await session.commit()

        # Create seats for room1
        for row in "ABCDE":
            for num in range(1, 11):
                seat = Seat(row=row, number=num, room_id=room1.id, seat_type="standard")
                session.add(seat)

        # Create seats for room2
        for row in "ABCDEFGH":
            for num in range(1, 11):
                seat = Seat(row=row, number=num, room_id=room2.id, seat_type="standard")
                session.add(seat)

        # Create sample movies
        movie1 = Movie(
            title="Inception",
            overview="A thief who enters the dreams of others to steal their secrets.",
            runtime=148,
            vote_average=8.8,
            poster_path="https://image.tmdb.org/t/p/w500/9gk7adHYeDvHkCSEqAvQNLV5Uge.jpg",
            backdrop_path="https://image.tmdb.org/t/p/original/s3TBrRGB1iav7gFOCNx3H31MoES.jpg",
            tmdb_id=27205,
        )
        session.add(movie1)

        movie2 = Movie(
            title="The Shawshank Redemption",
            overview=(
                "Two imprisoned men bond over a number of years, finding solace and eventual "
                + "redemption through acts of common decency."
            ),
            runtime=142,
            vote_average=9.3,
            poster_path="https://image.tmdb.org/t/p/w500/q6y0Go1tsGEsmtFryDOJo3dEmqu.jpg",
            backdrop_path="https://image.tmdb.org/t/p/original/kXfqcdQKsToO0OUXHcrrNCHDBzO.jpg",
            tmdb_id=278,
        )
        session.add(movie2)

        # Commit to get IDs
        await session.commit()

        # Create showings for the movies
        # For the next 7 days
        start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        for day in range(7):
            showing_date = start_date + timedelta(days=day)

            # Create showings for movie1 in room1
            for hour in [14, 17, 20]:
                showing = Showing(
                    movie_id=movie1.id,
                    room_id=room1.id,
                    start_time=showing_date.replace(hour=hour, minute=0),
                    end_time=showing_date.replace(hour=hour, minute=0)
                    + timedelta(minutes=random.randint(130, 160)),
                    price=random.uniform(8.99, 12.99),
                )
                session.add(showing)

            # Create showings for movie2 in room2
            for hour in [15, 18, 21]:
                showing = Showing(
                    movie_id=movie2.id,
                    room_id=room2.id,
                    start_time=showing_date.replace(hour=hour, minute=0),
                    end_time=showing_date.replace(hour=hour, minute=0)
                    + timedelta(minutes=random.randint(130, 160)),
                    price=random.uniform(8.99, 12.99),
                )
                session.add(showing)

        await session.commit()
        logger.info("Sample data created successfully!")


# This can be run directly for testing
if __name__ == "__main__":
    asyncio.run(create_sample_data())
