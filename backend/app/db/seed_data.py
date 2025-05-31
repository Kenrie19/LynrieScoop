import asyncio
import logging
import random
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.sql import text

from app.core.security import get_password_hash
from app.db.session import AsyncSessionLocal
from app.models.cinema import Cinema
from app.models.movie import Movie
from app.models.room import Room
from app.models.showing import Showing
from app.models.user import User

logger = logging.getLogger(__name__)

tmdb_movies = [
    {
        "adult": False,
        "backdrop_path": "/nAxGnGHOsfzufThz20zgmRwKur3.jpg",
        "genre_ids": [27, 53],
        "id": 1233413,
        "original_language": "en",
        "original_title": "Sinners",
        "overview": (
            "Trying to leave their troubled lives behind, twin brothers return to their "
            "hometown to start again, only to discover that an even greater evil is waiting "
            "to welcome them back."
        ),
        "popularity": 187.3789,
        "poster_path": "/Alhlf01RGavrTwQIByWW37T7WeY.jpg",
        "release_date": "2025-04-16",
        "title": "Sinners",
        "video": False,
        "vote_average": 7.5,
        "vote_count": 869,
    },
    {
        "adult": False,
        "backdrop_path": "/m9EtP1Yrzv6v7dMaC9mRaGhd1um.jpg",
        "genre_ids": [28, 878, 12],
        "id": 986056,
        "original_language": "en",
        "original_title": "Thunderbolts*",
        "overview": (
            "After finding themselves ensnared in a death trap, seven disillusioned castoffs "
            "must embark on a dangerous mission that will force them to confront the darkest "
            "corners of their pasts."
        ),
        "popularity": 127.6032,
        "poster_path": "/m9EtP1Yrzv6v7dMaC9mRaGhd1um.jpg",
        "release_date": "2025-04-30",
        "title": "Thunderbolts*",
        "video": False,
        "vote_average": 7.43,
        "vote_count": 1035,
    },
    {
        "adult": False,
        "backdrop_path": "/cJvUJEEQ86LSjl4gFLkYpdCJC96.jpg",
        "genre_ids": [10752, 28],
        "id": 1241436,
        "original_language": "en",
        "original_title": "Warfare",
        "overview": (
            "A platoon of Navy SEALs embarks on a dangerous mission in Ramadi, Iraq, with the "
            "chaos and brotherhood of war retold through their memories of the event."
        ),
        "popularity": 185.2449,
        "poster_path": "/srj9rYrjefyWqkLc6l2xjTGeBGO.jpg",
        "release_date": "2025-04-09",
        "title": "Warfare",
        "video": False,
        "vote_average": 7.302,
        "vote_count": 461,
    },
    {
        "adult": False,
        "backdrop_path": "/7Zx3wDG5bBtcfk8lcnCWDOLM4Y4.jpg",
        "genre_ids": [10751, 35, 878],
        "id": 552524,
        "original_language": "en",
        "original_title": "Lilo & Stitch",
        "overview": (
            "The wildly funny and touching story of a lonely Hawaiian girl and the fugitive "
            "alien who helps to mend her broken family."
        ),
        "popularity": 733.0556,
        "poster_path": "/3bN675X0K2E5QiAZVChzB5wq90B.jpg",
        "release_date": "2025-05-17",
        "title": "Lilo & Stitch",
        "video": False,
        "vote_average": 7.1,
        "vote_count": 334,
    },
    {
        "adult": False,
        "backdrop_path": "/z53D72EAOxGRqdr7KXXWp9dJiDe.jpg",
        "genre_ids": [28, 12, 53],
        "id": 575265,
        "original_language": "en",
        "original_title": "Mission: Impossible - The Final Reckoning",
        "overview": (
            "Ethan Hunt and team continue their search for the terrifying AI known as the "
            "Entity — which has infiltrated intelligence networks all over the globe — with "
            "the world's governments and a mysterious ghost from Hunt's past on their trail. "
            "Joined by new allies and armed with the means to shut the Entity down for good, "
            "Hunt is in a race against time to prevent the world as we know it from changing forever."
        ),
        "popularity": 286.3732,
        "poster_path": "/z53D72EAOxGRqdr7KXXWp9dJiDe.jpg",
        "release_date": "2025-05-17",
        "title": "Mission: Impossible - The Final Reckoning",
        "video": False,
        "vote_average": 7.1,
        "vote_count": 471,
    },
    {
        "adult": False,
        "backdrop_path": "/uIpJPDNFoeX0TVml9smPrs9KUVx.jpg",
        "genre_ids": [27, 9648],
        "id": 574475,
        "original_language": "en",
        "original_title": "Final Destination Bloodlines",
        "overview": (
            "Plagued by a violent recurring nightmare, college student Stefanie heads home to "
            "track down the one person who might be able to break the cycle and save her family "
            "from the grisly demise that inevitably awaits them all."
        ),
        "popularity": 364.4598,
        "poster_path": "/6WxhEvFsauuACfv8HyoVX6mZKFj.jpg",
        "release_date": "2025-05-14",
        "title": "Final Destination Bloodlines",
        "video": False,
        "vote_average": 7.035,
        "vote_count": 502,
    },
    {
        "adult": False,
        "backdrop_path": "/14UFWFJsGeInCbhTiehRLTff4Yx.jpg",
        "genre_ids": [53, 28],
        "id": 1233069,
        "original_language": "de",
        "original_title": "Exterritorial",
        "overview": (
            "When her son vanishes inside a US consulate, ex-special forces soldier Sara does "
            "everything in her power to find him — and uncovers a dark conspiracy."
        ),
        "popularity": 125.9771,
        "poster_path": "/jM2uqCZNKbiyStyzXOERpMqAbdx.jpg",
        "release_date": "2025-04-29",
        "title": "Exterritorial",
        "video": False,
        "vote_average": 6.734,
        "vote_count": 418,
    },
    {
        "adult": False,
        "backdrop_path": "/yFHHfHcUgGAxziP1C3lLt0q2T4s.jpg",
        "genre_ids": [10751, 35, 12, 14],
        "id": 950387,
        "original_language": "en",
        "original_title": "A Minecraft Movie",
        "overview": (
            "Four misfits find themselves struggling with ordinary problems when they are "
            "suddenly pulled through a mysterious portal into the Overworld: a bizarre, cubic "
            "wonderland that thrives on imagination. To get back home, they'll have to master "
            "this world while embarking on a magical quest with an unexpected, expert crafter, Steve."
        ),
        "popularity": 469.6691,
        "poster_path": "/yFHHfHcUgGAxziP1C3lLt0q2T4s.jpg",
        "release_date": "2025-03-31",
        "title": "A Minecraft Movie",
        "video": False,
        "vote_average": 6.504,
        "vote_count": 1550,
    },
    {
        "adult": False,
        "backdrop_path": "/juA4IWO52Fecx8lhAsxmDgy3M3.jpg",
        "genre_ids": [27, 9648],
        "id": 1232546,
        "original_language": "en",
        "original_title": "Until Dawn",
        "overview": (
            "One year after her sister Melanie mysteriously disappeared, Clover and her friends "
            "head into the remote valley where she vanished in search of answers. Exploring an "
            "abandoned visitor center, they find themselves stalked by a masked killer and "
            "horrifically murdered one by one...only to wake up and find themselves back at the "
            "beginning of the same evening."
        ),
        "popularity": 296.7954,
        "poster_path": "/juA4IWO52Fecx8lhAsxmDgy3M3.jpg",
        "release_date": "2025-04-23",
        "title": "Until Dawn",
        "video": False,
        "vote_average": 6.464,
        "vote_count": 498,
    },
]


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
            role="manager",
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
            description=("A premier cinema experience in the heart of the city"),
        )
        session.add(cinema)

        # Commit to get cinema ID
        await session.commit()

        # Make 5 rooms for the cinema
        rooms = [
            Room(
                name=f"Room {i}",
                capacity=random.randint(50, 100),
                has_3d=bool(i % 2),
                has_imax=bool((i + 1) % 2),
                cinema_id=cinema.id,
            )
            for i in range(1, 6)
        ]
        session.add_all(rooms)
        await session.commit()

        result = await session.execute(select(Room).where(Room.cinema_id == cinema.id))
        rooms = result.scalars().all()

        # Create sample movies from TMDB data
        for tmdb_movie in tmdb_movies:
            movie = Movie(
                title=tmdb_movie["title"],
                overview=tmdb_movie["overview"],
                runtime=random.randint(90, 180),
                vote_average=tmdb_movie["vote_average"],
                poster_path=tmdb_movie["poster_path"],
                backdrop_path=tmdb_movie["backdrop_path"],
                tmdb_id=tmdb_movie["id"],
                release_date=datetime.strptime(tmdb_movie["release_date"], "%Y-%m-%d"),
                genres=[str(genre) for genre in tmdb_movie.get("genre_ids", [])],
                vote_count=tmdb_movie["vote_count"],
            )
            session.add(movie)

        # Commit to get IDs
        await session.commit()

        result = await session.execute(select(Movie))
        movies = result.scalars().all()

        # Start date for showings
        start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        # Time slots for showings
        time_slots = [
            datetime.strptime(t, "%H:%M").time()
            for t in [
                "13:45",
                "14:00",
                "14:15",
                "16:30",
                "16:45",
                "19:30",
                "19:45",
                "21:30",
                "21:45",
            ]
        ]

        # Retrieve the added movies
        result = await session.execute(select(Movie))
        movies = result.scalars().all()

        # Mapping: tmdb_id -> Movie
        movie_map = {movie.tmdb_id: movie for movie in movies}

        # Helper: determine if a movie is family-friendly
        def is_family_friendly(tmdb_movie):
            return 10751 in tmdb_movie.get("genre_ids", []) or 16 in tmdb_movie.get("genre_ids", [])

        # For the next 7 days
        for day_offset in range(7):
            current_date = start_date + timedelta(days=day_offset)

            # For each room, keep track of which time slots are already booked
            room_schedule = {room.id: set() for room in rooms}

            # Sort family-friendly movies first, then the rest
            sorted_tmdb_movies = sorted(
                tmdb_movies, key=lambda m: (not is_family_friendly(m), -m["vote_average"])
            )

            for tmdb_movie in sorted_tmdb_movies:
                movie = movie_map.get(tmdb_movie["id"])
                if not movie:
                    continue

                # Choose preferred time slots based on genre
                if 27 in tmdb_movie["genre_ids"]:
                    preferred_slots = [(21, 30), (21, 45)]
                elif is_family_friendly(tmdb_movie):
                    preferred_slots = [(13, 45), (14, 0), (14, 15)]
                else:
                    preferred_slots = [(16, 30), (16, 45), (19, 30), (19, 45)]

                # Add other time slots as backup
                all_slots = preferred_slots + [t for t in time_slots if t not in preferred_slots]

                scheduled = False

                # Try to schedule in an available room
                for hour, minute in all_slots:
                    start_time = current_date.replace(hour=hour, minute=minute)
                    end_time = start_time + timedelta(minutes=movie.runtime or 120)

                    for room in rooms:
                        if (hour, minute) not in room_schedule[room.id]:
                            # Schedule the showing
                            showing = Showing(
                                movie_id=movie.id,
                                room_id=room.id,
                                start_time=start_time,
                                end_time=end_time,
                                status="scheduled",
                                price=12.50,  # Set default price to avoid NOT NULL violation
                            )
                            session.add(showing)
                            room_schedule[room.id].add((hour, minute))
                            scheduled = True
                            break

                    if scheduled:
                        break

                if not scheduled:
                    logger.warning(
                        f"Could not find a time slot for movie {movie.title} on {current_date.date()}"
                    )

        await session.commit()
        logger.info("Sample data created successfully!")


# This can be run directly for testing
if __name__ == "__main__":
    asyncio.run(create_sample_data())
