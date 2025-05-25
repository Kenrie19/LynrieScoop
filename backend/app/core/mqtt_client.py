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

import paho.mqtt.client as mqtt
from fastapi import FastAPI
from paho.mqtt.client import MQTTMessage

from app.core.config import settings

logger = logging.getLogger(__name__)

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
    user_id = payload.get("userId")
    showing_id = payload.get("showingId")
    seats = payload.get("seats", [])

    if not user_id or not showing_id or not seats:
        logger.error(f"Invalid booking request: {payload}")
        publish_message(
            f"booking/response/{user_id}",
            {"success": False, "message": "Invalid booking request"},
        )
        return

    logger.info(
        f"Processing booking request from user {user_id} for showing {showing_id}, seats: {seats}"
    )

    # TODO: Implement booking logic with database integration
    # This would:
    # 1. Check if seats are available
    # 2. Create a temporary reservation
    # 3. Process payment (or simulate it)
    # 4. Confirm the booking

    # For now, just send a success response
    success = True
    message = "Booking successful"

    # Publish result to user-specific topic
    publish_message(
        f"booking/response/{user_id}",
        {"success": success, "message": message, "bookingId": "123456"},
    )

    if success:
        # Publish seat updates to all clients
        for seat_id in seats:
            publish_message(
                "seats/updates",
                {
                    "showingId": showing_id,
                    "seatId": seat_id,
                    "status": "booked",
                    "updatedAt": "2025-05-01T12:00:00Z",
                    "userId": user_id,
                },
            )

        # Also publish to showing-specific topic
        for seat_id in seats:
            publish_message(
                f"showing/{showing_id}/seats",
                {
                    "seatId": seat_id,
                    "status": "booked",
                    "updatedAt": "2025-05-01T12:00:00Z",
                    "userId": user_id,
                },
            )


@handle_topic("seats/status/#")
def handle_seat_status(client: mqtt.Client, topic: str, payload: dict) -> None:
    """Handle seat status updates from admin/system"""
    showing_id = topic.split("/")[2] if len(topic.split("/")) > 2 else None

    if not showing_id:
        logger.error(f"Invalid seat status topic: {topic}")
        return

    logger.info(f"Received seat status update for showing {showing_id}: {payload}")

    # Forward the update to all clients
    publish_message("seats/updates", {"showingId": showing_id, **payload})
