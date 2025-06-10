"""
WebSocket routes for real-time updates.
"""

from typing import Dict, Any, Optional
import json
import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, status

from app.core.websocket_manager import get_websocket_manager

# Setup router
router = APIRouter()
logger = logging.getLogger(__name__)


@router.websocket("/ws/{topic}")
async def websocket_endpoint(websocket: WebSocket, topic: str):
    """
    WebSocket endpoint for real-time updates.

    Args:
        websocket: The WebSocket connection
        topic: The topic to subscribe to (e.g., "screenings/{id}/update")
    """
    manager = get_websocket_manager()
    await manager.connect(websocket, topic)

    try:
        while True:
            # Wait for messages from the client
            data = await websocket.receive_text()
            # You can process client messages here if needed
            # For now, we just log them
            logger.info(f"Received message from client on topic {topic}: {data}")
    except WebSocketDisconnect:
        # Handle client disconnect
        manager.disconnect(websocket, topic)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket, topic)
