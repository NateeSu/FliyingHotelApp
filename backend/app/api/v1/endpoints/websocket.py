"""
WebSocket API Endpoints (Phase 3)
Real-time communication for dashboard updates
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from typing import Optional
import logging
import uuid

from app.core.websocket import manager

logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/dashboard")
async def websocket_dashboard_endpoint(
    websocket: WebSocket,
    client_id: Optional[str] = Query(None, description="Optional client ID for reconnection")
):
    """
    WebSocket endpoint for dashboard real-time updates

    Events sent to clients:
        - room_status_changed: Room status updated
        - overtime_alert: Guest exceeded expected checkout time
        - check_in: New check-in completed
        - check_out: Guest checked out
        - notification: New notification created

    Message format:
    {
        "event": "event_name",
        "data": { ... event-specific data ... },
        "timestamp": "2024-01-15T10:30:00"
    }

    Query Parameters:
        - client_id: Optional client ID for reconnection tracking
    """
    # Generate client ID if not provided
    if not client_id:
        client_id = str(uuid.uuid4())

    # Accept connection
    await manager.connect(websocket, client_id)

    # Send welcome message
    await manager.send_personal_message(
        message={
            "event": "connected",
            "data": {
                "client_id": client_id,
                "message": "เชื่อมต่อสำเร็จ"
            }
        },
        client_id=client_id
    )

    try:
        # Keep connection alive and handle incoming messages
        while True:
            # Receive message from client
            data = await websocket.receive_json()

            # Handle ping/pong for connection health check
            if data.get("type") == "ping":
                await manager.send_personal_message(
                    message={"type": "pong"},
                    client_id=client_id
                )
                continue

            # Log other messages (future: could handle client commands)
            logger.info(f"Received message from {client_id}: {data}")

    except WebSocketDisconnect:
        manager.disconnect(client_id)
        logger.info(f"Client {client_id} disconnected")

    except Exception as e:
        logger.error(f"WebSocket error for client {client_id}: {e}")
        manager.disconnect(client_id)


@router.get("/connections")
async def get_active_connections():
    """
    Get number of active WebSocket connections

    This is a helper endpoint for monitoring.

    Returns:
        {"active_connections": int}
    """
    return {"active_connections": manager.get_active_connections_count()}
