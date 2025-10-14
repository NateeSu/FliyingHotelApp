"""
WebSocket Manager (Phase 3)
Manages WebSocket connections and broadcasts for real-time updates
"""
from typing import Dict, Set
from fastapi import WebSocket
import json
import logging
from datetime import datetime
from app.core.datetime_utils import now_thailand

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    WebSocket Connection Manager
    Manages multiple WebSocket connections and handles broadcasting
    """

    def __init__(self):
        # Store active connections by connection ID
        self.active_connections: Dict[str, WebSocket] = {}
        # Store connections by room (for future use)
        self.room_connections: Dict[str, Set[str]] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"WebSocket connected: {client_id}. Total connections: {len(self.active_connections)}")

    def disconnect(self, client_id: str):
        """Remove a WebSocket connection"""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            logger.info(f"WebSocket disconnected: {client_id}. Total connections: {len(self.active_connections)}")

        # Remove from all rooms
        for room_id, connections in self.room_connections.items():
            if client_id in connections:
                connections.remove(client_id)

    async def send_personal_message(self, message: dict, client_id: str):
        """Send a message to a specific client"""
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_json(message)
            except Exception as e:
                logger.error(f"Error sending message to {client_id}: {e}")
                self.disconnect(client_id)

    async def broadcast(self, message: dict, exclude_client: str = None):
        """
        Broadcast a message to all connected clients

        Args:
            message: Dictionary containing the message data
            exclude_client: Optional client ID to exclude from broadcast
        """
        # Add timestamp if not present (using Thailand timezone)
        if "timestamp" not in message:
            message["timestamp"] = now_thailand().isoformat()

        disconnected_clients = []

        for client_id, connection in self.active_connections.items():
            if exclude_client and client_id == exclude_client:
                continue

            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to {client_id}: {e}")
                disconnected_clients.append(client_id)

        # Clean up disconnected clients
        for client_id in disconnected_clients:
            self.disconnect(client_id)

    async def broadcast_room_status_change(self, room_id: int, old_status: str, new_status: str, room_data: dict = None):
        """
        Broadcast room status change event

        Args:
            room_id: ID of the room
            old_status: Previous status
            new_status: New status
            room_data: Additional room data to broadcast
        """
        message = {
            "event": "room_status_changed",
            "data": {
                "room_id": room_id,
                "old_status": old_status,
                "new_status": new_status,
                "room_data": room_data or {}
            }
        }
        await self.broadcast(message)
        logger.info(f"Broadcasted room status change: Room {room_id} {old_status} → {new_status}")

    async def broadcast_overtime_alert(self, room_id: int, room_number: str, guest_name: str, overtime_minutes: int, stay_type: str):
        """
        Broadcast overtime alert event

        Args:
            room_id: ID of the room
            room_number: Room number
            guest_name: Guest name
            overtime_minutes: Minutes overtime
            stay_type: Type of stay (overnight/temporary)
        """
        message = {
            "event": "overtime_alert",
            "data": {
                "room_id": room_id,
                "room_number": room_number,
                "guest_name": guest_name,
                "overtime_minutes": overtime_minutes,
                "stay_type": stay_type
            }
        }
        await self.broadcast(message)
        logger.info(f"Broadcasted overtime alert: Room {room_number}, {overtime_minutes} minutes")

    async def broadcast_check_in(self, room_id: int, room_number: str, customer_name: str, stay_type: str):
        """Broadcast check-in event"""
        message = {
            "event": "check_in",
            "data": {
                "room_id": room_id,
                "room_number": room_number,
                "customer_name": customer_name,
                "stay_type": stay_type
            }
        }
        await self.broadcast(message)
        logger.info(f"Broadcasted check-in: Room {room_number}")

    async def broadcast_check_out(self, room_id: int, room_number: str):
        """Broadcast check-out event"""
        message = {
            "event": "check_out",
            "data": {
                "room_id": room_id,
                "room_number": room_number
            }
        }
        await self.broadcast(message)
        logger.info(f"Broadcasted check-out: Room {room_number}")

    async def broadcast_notification(self, notification_type: str, target_role: str, title: str, message_text: str, room_id: int = None):
        """
        Broadcast notification event

        Args:
            notification_type: Type of notification
            target_role: Target role for notification
            title: Notification title
            message_text: Notification message
            room_id: Optional room ID
        """
        message = {
            "event": "notification",
            "data": {
                "notification_type": notification_type,
                "target_role": target_role,
                "title": title,
                "message": message_text,
                "room_id": room_id
            }
        }
        await self.broadcast(message)
        logger.info(f"Broadcasted notification: {notification_type} to {target_role}")

    def get_active_connections_count(self) -> int:
        """Get the number of active connections"""
        return len(self.active_connections)


# Global connection manager instance
manager = ConnectionManager()
