# backend/app/api/routes/websocket_route.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.core.websocket_manager import connect_client, disconnect_client

router = APIRouter()


@router.websocket("/ws/seats")
async def websocket_endpoint(websocket: WebSocket):
    await connect_client(websocket)
    try:
        while True:
            await websocket.receive_text()  # (optioneel)
    except WebSocketDisconnect:
        disconnect_client(websocket)
