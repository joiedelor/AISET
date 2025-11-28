"""
WebSocket Manager Service
DO-178C Traceability: REQ-FE-005 (Real-time updates via WebSocket)

This service manages WebSocket connections for real-time process updates.
Upgrades the ProcessEventService from in-memory to WebSocket broadcasting.

Features:
- WebSocket connection management
- Room-based broadcasting (per project/CI)
- Integration with ProcessEventService
- Automatic reconnection handling
"""

from typing import Dict, Set, Any
from datetime import datetime
import logging
import socketio
from fastapi import FastAPI

logger = logging.getLogger(__name__)


class WebSocketManager:
    """
    Manages WebSocket connections for real-time updates.

    Uses Socket.IO for reliable WebSocket communication with
    fallback to long-polling if WebSocket unavailable.
    """

    def __init__(self):
        """Initialize WebSocket manager."""
        # Create Socket.IO server with CORS
        self.sio = socketio.AsyncServer(
            async_mode='asgi',
            cors_allowed_origins='*',  # Configure appropriately for production
            logger=True,
            engineio_logger=True
        )

        # Track connections by project and CI
        self.project_rooms: Dict[int, Set[str]] = {}  # project_id -> set of sids
        self.ci_rooms: Dict[int, Set[str]] = {}  # ci_id -> set of sids

        # Register event handlers
        self._register_handlers()

        logger.info("WebSocket manager initialized")

    def _register_handlers(self):
        """Register Socket.IO event handlers."""

        @self.sio.event
        async def connect(sid, environ):
            """Handle client connection."""
            logger.info(f"WebSocket client connected: {sid}")
            await self.sio.emit('connection_established', {
                'timestamp': datetime.utcnow().isoformat(),
                'message': 'Connected to AISET real-time updates'
            }, room=sid)

        @self.sio.event
        async def disconnect(sid):
            """Handle client disconnection."""
            logger.info(f"WebSocket client disconnected: {sid}")

            # Remove from all rooms
            for project_id, sids in list(self.project_rooms.items()):
                if sid in sids:
                    sids.remove(sid)
                    if not sids:
                        del self.project_rooms[project_id]

            for ci_id, sids in list(self.ci_rooms.items()):
                if sid in sids:
                    sids.remove(sid)
                    if not sids:
                        del self.ci_rooms[ci_id]

        @self.sio.event
        async def subscribe_project(sid, data):
            """Subscribe to project updates."""
            project_id = data.get('project_id')
            if project_id:
                if project_id not in self.project_rooms:
                    self.project_rooms[project_id] = set()

                self.project_rooms[project_id].add(sid)
                await self.sio.enter_room(sid, f'project_{project_id}')

                logger.info(f"Client {sid} subscribed to project {project_id}")
                await self.sio.emit('subscription_confirmed', {
                    'type': 'project',
                    'id': project_id
                }, room=sid)

        @self.sio.event
        async def subscribe_ci(sid, data):
            """Subscribe to CI updates."""
            ci_id = data.get('ci_id')
            if ci_id:
                if ci_id not in self.ci_rooms:
                    self.ci_rooms[ci_id] = set()

                self.ci_rooms[ci_id].add(sid)
                await self.sio.enter_room(sid, f'ci_{ci_id}')

                logger.info(f"Client {sid} subscribed to CI {ci_id}")
                await self.sio.emit('subscription_confirmed', {
                    'type': 'ci',
                    'id': ci_id
                }, room=sid)

        @self.sio.event
        async def unsubscribe_project(sid, data):
            """Unsubscribe from project updates."""
            project_id = data.get('project_id')
            if project_id and project_id in self.project_rooms:
                self.project_rooms[project_id].discard(sid)
                await self.sio.leave_room(sid, f'project_{project_id}')
                logger.info(f"Client {sid} unsubscribed from project {project_id}")

        @self.sio.event
        async def unsubscribe_ci(sid, data):
            """Unsubscribe from CI updates."""
            ci_id = data.get('ci_id')
            if ci_id and ci_id in self.ci_rooms:
                self.ci_rooms[ci_id].discard(sid)
                await self.sio.leave_room(sid, f'ci_{ci_id}')
                logger.info(f"Client {sid} unsubscribed from CI {ci_id}")

    async def broadcast_activity_completed(
        self,
        ci_id: int,
        activity_id: str,
        activity_name: str,
        progress_percent: float
    ):
        """Broadcast activity completion to subscribed clients."""
        event_data = {
            "type": "activity_completed",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "ci_id": ci_id,
                "activity_id": activity_id,
                "activity_name": activity_name,
                "progress_percent": progress_percent
            }
        }

        await self.sio.emit('process_event', event_data, room=f'ci_{ci_id}')
        logger.info(f"Broadcasted activity_completed for CI {ci_id}")

    async def broadcast_activity_started(
        self,
        ci_id: int,
        activity_id: str,
        activity_name: str
    ):
        """Broadcast activity start to subscribed clients."""
        event_data = {
            "type": "activity_started",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "ci_id": ci_id,
                "activity_id": activity_id,
                "activity_name": activity_name
            }
        }

        await self.sio.emit('process_event', event_data, room=f'ci_{ci_id}')
        logger.info(f"Broadcasted activity_started for CI {ci_id}")

    async def broadcast_phase_completed(
        self,
        ci_id: int,
        phase_id: str,
        phase_name: str,
        progress_percent: float
    ):
        """Broadcast phase completion to subscribed clients."""
        event_data = {
            "type": "phase_completed",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "ci_id": ci_id,
                "phase_id": phase_id,
                "phase_name": phase_name,
                "progress_percent": progress_percent
            }
        }

        await self.sio.emit('process_event', event_data, room=f'ci_{ci_id}')
        logger.info(f"Broadcasted phase_completed for CI {ci_id}")

    async def broadcast_progress_updated(self, ci_id: int, progress_percent: float):
        """Broadcast progress update to subscribed clients."""
        event_data = {
            "type": "progress_updated",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "ci_id": ci_id,
                "progress_percent": progress_percent
            }
        }

        await self.sio.emit('process_event', event_data, room=f'ci_{ci_id}')
        logger.debug(f"Broadcasted progress_updated for CI {ci_id}")

    async def broadcast_to_project(self, project_id: int, event_type: str, data: Dict[str, Any]):
        """
        Broadcast arbitrary event to all clients subscribed to a project.

        Args:
            project_id: Project ID
            event_type: Type of event
            data: Event data
        """
        event_data = {
            "type": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data
        }

        await self.sio.emit('project_event', event_data, room=f'project_{project_id}')
        logger.info(f"Broadcasted {event_type} to project {project_id}")

    def get_asgi_app(self, app: FastAPI):
        """
        Get the ASGI app for mounting to FastAPI.

        Args:
            app: FastAPI application instance

        Returns:
            Socket.IO ASGI app
        """
        return socketio.ASGIApp(self.sio, app)


# Global instance
_websocket_manager = None


def get_websocket_manager() -> WebSocketManager:
    """Get global WebSocket manager instance."""
    global _websocket_manager
    if _websocket_manager is None:
        _websocket_manager = WebSocketManager()
    return _websocket_manager


def init_websocket_manager(app: FastAPI):
    """
    Initialize WebSocket manager and mount to FastAPI app.

    Args:
        app: FastAPI application instance
    """
    manager = get_websocket_manager()
    return manager.get_asgi_app(app)
