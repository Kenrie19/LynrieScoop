"""
WebSocket manager for the LynrieScoop cinema application.

This module provides WebSocket functionality for real-time messaging,
including connection management, broadcasting messages, and handling
client connections.
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional
from uuid import UUID

from fastapi import WebSocket, WebSocketDisconnect
from fastapi.encoders import jsonable_encoder

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    WebSocket connection manager for the application.

    Handles client connections, disconnections, and message broadcasting.
    """

    def __init__(self):
        # Map of topic -> list of connected websockets
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, topic: str):
        """
        Connect a client to a specific topic.

        Args:
            websocket: The WebSocket connection
            topic: The topic to subscribe to
        """
        await websocket.accept()
        if topic not in self.active_connections:
            self.active_connections[topic] = []
        self.active_connections[topic].append(websocket)
        logger.info(f"Client connected to topic: {topic}")

    def disconnect(self, websocket: WebSocket, topic: str):
        """
        Disconnect a client from a topic.

        Args:
            websocket: The WebSocket connection to disconnect
            topic: The topic to unsubscribe from
        """
        if topic in self.active_connections:
            if websocket in self.active_connections[topic]:
                self.active_connections[topic].remove(websocket)
                logger.info(f"Client disconnected from topic: {topic}")

            # Clean up empty topics
            if not self.active_connections[topic]:
                del self.active_connections[topic]

    async def broadcast(self, topic: str, message: Any):
        """
        Broadcast a message to all clients subscribed to a topic.

        Args:
            topic: The topic to broadcast to
            message: The message to send (will be JSON serialized)
        """
        if topic not in self.active_connections:
            return

        # Serialize the message to JSON
        json_message = json.dumps(jsonable_encoder(message))

        # Send the message to all connected clients for this topic
        disconnected_clients = []
        for websocket in self.active_connections[topic]:
            try:
                await websocket.send_text(json_message)
            except Exception as e:
                logger.error(f"Failed to send message: {e}")
                disconnected_clients.append(websocket)

        # Clean up disconnected clients
        for websocket in disconnected_clients:
            self.disconnect(websocket, topic)


# Singleton instance
manager = ConnectionManager()


def get_websocket_manager() -> ConnectionManager:
    """
    Get the WebSocket connection manager singleton.

    Returns:
        The WebSocket connection manager instance
    """
    return manager
