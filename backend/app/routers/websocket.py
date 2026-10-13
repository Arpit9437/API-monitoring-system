from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.websocket_manager import connection_manager

router = APIRouter(tags=["websocket"])


@router.websocket("/ws/monitors")
async def monitor_events(websocket: WebSocket) -> None:
    await connection_manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        connection_manager.disconnect(websocket)
