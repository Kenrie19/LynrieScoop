# backend/app/core/websocket_manager.py
from fastapi import WebSocket
from typing import List

connected_clients: List[WebSocket] = []


async def connect_client(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)


def disconnect_client(websocket: WebSocket):
    if websocket in connected_clients:
        connected_clients.remove(websocket)


async def broadcast_json(data: dict):
    for client in connected_clients:
        await client.send_json(data)
