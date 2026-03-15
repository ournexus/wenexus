"""
util.websocket - WebSocket connection management for real-time updates.

Handles: Connection lifecycle, message broadcasting, client state.

Depends: fastapi, typing
Consumers: facade.roundtable
"""

from fastapi import WebSocket


class ConnectionManager:
    """Manage WebSocket connections for a discussion session."""

    def __init__(self) -> None:
        # session_id -> set of WebSocket connections
        self.active_connections: dict[str, set[WebSocket]] = {}

    async def connect(self, session_id: str, websocket: WebSocket) -> None:
        """Register a new WebSocket connection for a session."""
        await websocket.accept()
        if session_id not in self.active_connections:
            self.active_connections[session_id] = set()
        self.active_connections[session_id].add(websocket)

    def disconnect(self, session_id: str, websocket: WebSocket) -> None:
        """Remove a WebSocket connection."""
        if session_id in self.active_connections:
            self.active_connections[session_id].discard(websocket)
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]

    async def broadcast(self, session_id: str, message: dict) -> None:
        """Send a message to all connected clients for a session."""
        if session_id not in self.active_connections:
            return

        # Send to all connected clients
        disconnected = set()
        for connection in self.active_connections[session_id]:
            try:
                await connection.send_json(message)
            except Exception:
                # Mark for removal if send fails
                disconnected.add(connection)

        # Clean up disconnected clients
        for connection in disconnected:
            self.disconnect(session_id, connection)

    def get_connection_count(self, session_id: str) -> int:
        """Get number of active connections for a session."""
        return len(self.active_connections.get(session_id, set()))


# Global connection manager instance
ws_manager = ConnectionManager()
