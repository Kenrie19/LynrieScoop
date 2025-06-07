import asyncio
import logging
import random
from collections import defaultdict
from datetime import datetime, time, timedelta
from typing import Any, Dict, List, Set, Tuple, cast
from uuid import UUID

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
        "tmdb_id": 1233413,
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
        "runtime": 138,
    },
    {
        "adult": False,
        "backdrop_path": "/m9EtP1Yrzv6v7dMaC9mRaGhd1um.jpg",
        "genre_ids": [28, 878, 12],
        "tmdb_id": 986056,
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
        "runtime": 127,
    },
    {
        "adult": False,
        "backdrop_path": "/cJvUJEEQ86LSjl4gFLkYpdCJC96.jpg",
        "genre_ids": [10752, 28],
        "tmdb_id": 1241436,
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
        "runtime": 95,
    },
    {
        "adult": False,
        "backdrop_path": "/7Zx3wDG5bBtcfk8lcnCWDOLM4Y4.jpg",
        "genre_ids": [10751, 35, 878],
        "tmdb_id": 552524,
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
        "runtime": 108,
    },
    {
        "adult": False,
        "backdrop_path": "/z53D72EAOxGRqdr7KXXWp9dJiDe.jpg",
        "genre_ids": [28, 12, 53],
        "tmdb_id": 575265,
        "original_language": "en",
        "original_title": "Mission: Impossible - The Final Reckoning",
        "overview": (
            "Ethan Hunt and team continue their search for the terrifying AI known as the "
            "Entity — which has infiltrated intelligence networks all over the globe — with "
            "the world's governments and a mysterious ghost from Hunt's past on their trail. "
            "Joined by new allies and armed with the means to shut the Entity down for good, "
            "Hunt is in a race against time to prevent the world as we know it from changing"
            " forever."
        ),
        "popularity": 286.3732,
        "poster_path": "/z53D72EAOxGRqdr7KXXWp9dJiDe.jpg",
        "release_date": "2025-05-17",
        "title": "Mission: Impossible - The Final Reckoning",
        "video": False,
        "vote_average": 7.1,
        "vote_count": 471,
        "runtime": 170,
    },
    {
        "adult": False,
        "backdrop_path": "/uIpJPDNFoeX0TVml9smPrs9KUVx.jpg",
        "genre_ids": [27, 9648],
        "tmdb_id": 574475,
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
        "runtime": 110,
    },
    {
        "adult": False,
        "backdrop_path": "/yFHHfHcUgGAxziP1C3lLt0q2T4s.jpg",
        "genre_ids": [10751, 35, 12, 14],
        "tmdb_id": 950387,
        "original_language": "en",
        "original_title": "A Minecraft Movie",
        "overview": (
            "Four misfits find themselves struggling with ordinary problems when they are "
            "suddenly pulled through a mysterious portal into the Overworld: a bizarre, cubic "
            "wonderland that thrives on imagination. To get back home, they'll have to master "
            "this world while embarking on a magical quest with an unexpected, expert crafter,"
            " Steve."
        ),
        "popularity": 469.6691,
        "poster_path": "/yFHHfHcUgGAxziP1C3lLt0q2T4s.jpg",
        "release_date": "2025-03-31",
        "title": "A Minecraft Movie",
        "video": False,
        "vote_average": 6.504,
        "vote_count": 1550,
        "runtime": 101,
    },
]


def to_uuid(val: Any) -> UUID:
    return UUID(str(val)) if not isinstance(val, UUID) else val


def to_int(val: Any) -> int:
    try:
        return int(val)
    except Exception:
        return int(str(val).replace("-", "")[0:12], 16)  # fallback for UUIDs


async def create_sample_data() -> None:
    logger.info("Creating sample data...")

    async with AsyncSessionLocal() as session:
        result = await session.execute(text("SELECT COUNT(*) FROM users"))
        user_count = result.scalar()

        if user_count and user_count > 0:
            logger.info("Sample data already exists, skipping...")
            return

        # Users
        admin_user = User(
            email="admin@cinema.com",
            hashed_password=get_password_hash("admin"),
            role="manager",
            name="Admin User",
        )
        regular_user = User(
            email="user@cinema.com",
            hashed_password=get_password_hash("password"),
            role="user",
            name="Regular User",
        )
        session.add_all([admin_user, regular_user])

        # Cinema
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
        await session.commit()

        # Rooms
        temp_rooms = [
            Room(
                name=f"Room {i}",
                capacity=random.randint(50, 100),
                has_3d=bool(i % 2),
                has_imax=bool((i + 1) % 2),
                cinema_id=cinema.id,
            )
            for i in range(1, 6)
        ]
        session.add_all(temp_rooms)
        await session.commit()

        # Retrieve persisted Room objects
        result = await session.execute(select(Room).where(Room.cinema_id == cinema.id))
        rooms = cast(List[Room], list(result.scalars()))  # type: ignore

        # Movies
        for tmdb_movie in tmdb_movies:
            movie = Movie(
                title=tmdb_movie["title"],
                overview=tmdb_movie["overview"],
                runtime=tmdb_movie.get("runtime", random.randint(90, 120)),
                vote_average=tmdb_movie["vote_average"],
                poster_path=tmdb_movie["poster_path"],
                backdrop_path=tmdb_movie["backdrop_path"],
                tmdb_id=tmdb_movie["tmdb_id"],
                release_date=datetime.strptime(str(tmdb_movie["release_date"]), "%Y-%m-%d"),
                genres=[str(genre) for genre in cast(List[int], tmdb_movie.get("genre_ids", []))],
                vote_count=tmdb_movie["vote_count"],
            )
            session.add(movie)
        await session.commit()

        result = await session.execute(select(Movie))
        movies = cast(List[Movie], list(result.scalars()))  # type: ignore
        movie_map: Dict[int, Movie] = {
            to_int(movie.tmdb_id): movie for movie in movies if movie.tmdb_id is not None
        }

        def is_family_friendly(movie_data: Dict[str, Any]) -> bool:
            return 10751 in movie_data.get("genre_ids", []) or 16 in movie_data.get("genre_ids", [])

        time_slots: List[time] = [
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
        afternoon_slots = {t for t in time_slots if t < time(17, 0)}
        start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        for day_offset in range(7):
            current_date = start_date + timedelta(days=day_offset)
            room_schedule: Dict[UUID, List[Tuple[datetime, datetime]]] = {
                to_uuid(room.id): [] for room in rooms
            }
            movie_counts: Dict[int, int] = {to_int(m["tmdb_id"]): 0 for m in tmdb_movies}
            scheduled_movies_per_slot: Dict[datetime, Set[int]] = defaultdict(set)

            for slot in time_slots:
                start_time = current_date.replace(hour=slot.hour, minute=slot.minute)
                random.shuffle(rooms)

                for room in rooms:
                    room_key = to_uuid(room.id)
                    if any(s <= start_time < e for s, e in room_schedule[room_key]):
                        continue

                    eligible_movies = []
                    for m in tmdb_movies:
                        tmdb_id = cast(int, m["tmdb_id"])
                        if (
                            movie_counts[tmdb_id] < 3
                            and movie_map[tmdb_id].id not in scheduled_movies_per_slot[start_time]
                        ):
                            eligible_movies.append(m)

                    if slot in afternoon_slots:
                        eligible_movies.sort(
                            key=lambda m: (
                                not is_family_friendly(m),
                                -float(str(m["vote_average"])),
                            )
                        )
                    else:
                        eligible_movies.sort(key=lambda m: -float(str(m["vote_average"])))

                    for m in eligible_movies:
                        movie_ = movie_map.get(to_int(m["tmdb_id"]))
                        if movie_ is None:
                            continue

                        runtime = int(movie.runtime or 120)
                        end_time = start_time + timedelta(minutes=runtime)

                        if any(
                            not (end_time <= s or start_time >= e)
                            for s, e in room_schedule[room_key]
                        ):
                            continue

                        session.add(
                            Showing(
                                movie_id=movie_.id,
                                room_id=room.id,
                                start_time=start_time,
                                end_time=end_time,
                                status="scheduled",
                                price=12.50,
                            )
                        )
                        room_schedule[room_key].append((start_time, end_time))
                        movie_counts[to_int(m["tmdb_id"])] += 1
                        scheduled_movies_per_slot[start_time].add(to_int(movie.id))  # type: ignore
                        break

        await session.commit()
        logger.info("Sample data created successfully!")


if __name__ == "__main__":
    asyncio.run(create_sample_data())
