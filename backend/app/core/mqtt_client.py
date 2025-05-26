"""
MQTT client integration for the LynrieScoop cinema application.

This module provides MQTT client functionality for real-time messaging,
including client initialization, connection management, message publishing,
and topic subscription with handler registration.
"""

import json
import logging
from functools import wraps
from typing import Any, Callable, Dict
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.models import Showing, Booking

import uuid
from uuid import UUID

import paho.mqtt.client as mqtt
from fastapi import FastAPI
from paho.mqtt.client import MQTTMessage
from app.core.config import settings

logger = logging.getLogger(__name__)
# Convert PostgresDsn to string and use asyncpg driver
postgres_url = str(settings.DATABASE_URL)
async_postgres_url = postgres_url.replace("postgresql://", "postgresql+asyncpg://")
engine = create_async_engine(async_postgres_url)
async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

# MQTT client singleton
_mqtt_client: mqtt.Client | None = None

# Topic handlers
_topic_handlers: dict[str, Callable[[mqtt.Client, str, Dict[str, Any]], None]] = {}


def get_mqtt_client() -> mqtt.Client:
    """
    Get the MQTT client singleton instance.

    Returns:
        mqtt.Client: The initialized MQTT client instance

    Note:
        Initializes the client if it doesn't already exist
    """
    global _mqtt_client
    if _mqtt_client is None:
        return init_mqtt_client()
    return _mqtt_client


def init_mqtt_client() -> mqtt.Client:
    """
    Initialize and configure the MQTT client.

    Returns:
        mqtt.Client: The newly initialized MQTT client

    Note:
        Sets up connection callbacks and MQTT broker configuration
    """
    global _mqtt_client

    if _mqtt_client is not None:
        return _mqtt_client

    broker_host = settings.MQTT_BROKER
    broker_port = settings.MQTT_PORT

    client = mqtt.Client(client_id=f"cinema-backend-{settings.ENVIRONMENT}")

    # Set up callbacks
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect

    try:
        logger.info(f"Connecting to MQTT broker at {broker_host}:{broker_port}")
        client.connect(broker_host, broker_port)
        client.loop_start()
        _mqtt_client = client
    except Exception as e:
        logger.error(f"Failed to connect to MQTT broker: {e}")
        raise

    return _mqtt_client


def on_connect(client: mqtt.Client, userdata: Any, flags: dict, rc: int) -> None:
    """Callback for when the client connects to the broker"""
    if rc == 0:
        logger.info("Connected to MQTT broker")

        # Subscribe to topics
        client.subscribe("booking/request")
        client.subscribe("seats/status/#")
        logger.info("Subscribed to booking and seat topics")
    else:
        logger.error(f"Failed to connect to MQTT broker with code {rc}")


def on_message(client: mqtt.Client, userdata: Any, msg: MQTTMessage) -> None:
    """Callback for when a message is received from the broker"""
    topic = msg.topic
    try:
        payload = json.loads(msg.payload.decode())
        logger.debug(f"Received message on topic {topic}: {payload}")

        # Call the appropriate handler for the topic
        for pattern, handler in _topic_handlers.items():
            if mqtt.topic_matches_sub(pattern, topic):
                handler(client, topic, payload)
                break
        else:
            logger.warning(f"No handler for topic {topic}")
    except json.JSONDecodeError:
        logger.error(f"Failed to decode message payload for topic {topic}")
    except Exception as e:
        logger.exception(f"Error handling message for topic {topic}: {e}")


def on_disconnect(client: mqtt.Client, userdata: Any, rc: int) -> None:
    """Callback for when the client disconnects from the broker"""
    if rc != 0:
        logger.warning(f"Unexpected disconnection from MQTT broker with code {rc}")
    else:
        logger.info("Disconnected from MQTT broker")


def handle_topic(topic_pattern: str) -> Callable:
    """Decorator to register a handler for a specific MQTT topic pattern"""

    def decorator(
        func: Callable[[mqtt.Client, str, Dict[str, Any]], None],
    ) -> Callable[[mqtt.Client, str, Dict[str, Any]], None]:
        _topic_handlers[topic_pattern] = func

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> None:
            return func(*args, **kwargs)

        return wrapper

    return decorator


def publish_message(
    topic: str, payload: Dict[str, Any], qos: int = 0, retain: bool = False
) -> bool:
    """Publish a message to the MQTT broker"""
    client = get_mqtt_client()
    if client is None:
        logger.error("Cannot publish message: MQTT client not initialized")
        return False

    try:
        message = json.dumps(payload)
        result = client.publish(topic, message, qos=qos, retain=retain)
        if result.rc != mqtt.MQTT_ERR_SUCCESS:
            logger.error(f"Failed to publish message to {topic}: {mqtt.error_string(result.rc)}")
            return False
        logger.debug(f"Published message to {topic}: {message}")
        return True
    except Exception as e:
        logger.error(f"Error publishing message to {topic}: {e}")
        return False


def setup_mqtt_for_app(app: FastAPI) -> None:
    """Set up MQTT client for the FastAPI application lifecycle"""

    @app.on_event("startup")
    def startup_mqtt_client() -> None:
        """Initialize MQTT client on application startup"""
        logger.info("Initializing MQTT client on application startup")
        init_mqtt_client()

    @app.on_event("shutdown")
    def shutdown_mqtt_client() -> None:
        """Stop MQTT client on application shutdown"""
        logger.info("Stopping MQTT client on application shutdown")
        client = get_mqtt_client()
        if client is not None:
            client.loop_stop()
            client.disconnect()
            logger.info("MQTT client disconnected")


# Topic handlers for specific MQTT topics
@handle_topic("booking/request")
def handle_booking_request(client: mqtt.Client, topic: str, payload: dict) -> None:
    """Handle booking requests from clients"""

    async def process_booking():
        user_id = payload.get("userId")
        showing_id = payload.get("showingId")

        if not user_id or not showing_id:
            logger.error(f"Invalid booking request: {payload}")
            publish_message(
                f"booking/response/{user_id}",
                {"success": False, "message": "Invalid booking request"},
            )
            return

        async with async_session() as db:
            result = await db.execute(
                select(Showing)
                .options(joinedload(Showing.room), joinedload(Showing.movie))
                .filter(Showing.id == UUID(showing_id))
            )
            showing = result.scalars().first()

            if not showing:
                publish_message(
                    f"booking/response/{user_id}",
                    {"success": False, "message": "Screening not found"},
                )
                return

            if showing.bookings_count >= showing.room.capacity:
                publish_message(
                    f"booking/response/{user_id}",
                    {"success": False, "message": "No tickets available"},
                )
                return

            booking = Booking(
                id=uuid.uuid4(),
                user_id=UUID(user_id),
                showing_id=showing.id,
                booking_number=str(uuid.uuid4())[:8].upper(),
                total_price=showing.price,
                status="confirmed",
            )

            db.add(booking)
            showing.bookings_count += 1
            await db.commit()

            # MQTT feedback
            remaining = showing.room.capacity - showing.bookings_count
            publish_message(
                f"screenings/{showing_id}/update",
                {
                    "screening_id": showing_id,
                    "available_tickets": remaining,
                    "total_capacity": showing.room.capacity,
                },
            )

            publish_message(
                f"booking/response/{user_id}",
                {
                    "success": True,
                    "message": "Booking successful",
                    "bookingId": str(booking.id),
                    "movie_title": showing.movie.title if showing.movie else "Unknown",
                    "start_time": showing.start_time.isoformat(),
                    "room": showing.room.name if showing.room else "Unknown",
                    "status": "confirmed",
                },
            )

    # Schedule the coroutine on the main event loop
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.run_coroutine_threadsafe(process_booking(), loop)
        else:
            loop.run_until_complete(process_booking())
    except RuntimeError:
        # If no event loop is running, create a new one (for safety in rare cases)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(process_booking())
