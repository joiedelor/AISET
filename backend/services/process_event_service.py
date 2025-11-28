"""
Process Event Service
DO-178C Traceability: REQ-SM-001, REQ-FE-005 (Real-time updates via WebSocket)

This service broadcasts process events for real-time UI updates.
Upgraded to use WebSocket for production-ready real-time communication.

Events:
- activity_completed
- activity_started
- phase_completed
- progress_updated
"""

from typing import Dict, List, Any, Callable, Optional
from datetime import datetime
import logging
import asyncio

logger = logging.getLogger(__name__)


class ProcessEventService:
    """
    Event service for process updates with WebSocket support.

    This service provides dual-mode operation:
    1. In-memory callbacks for local event handling
    2. WebSocket broadcast for real-time client updates
    """

    def __init__(self):
        self._listeners: Dict[str, List[Callable]] = {}
        self._websocket_manager = None  # Lazy loaded to avoid circular import

    def subscribe(self, event_type: str, callback: Callable):
        """
        Subscribe to an event type.

        Args:
            event_type: Type of event (e.g., 'activity_completed')
            callback: Function to call when event occurs
        """
        if event_type not in self._listeners:
            self._listeners[event_type] = []

        self._listeners[event_type].append(callback)
        logger.debug(f"Subscribed to event: {event_type}")

    def unsubscribe(self, event_type: str, callback: Callable):
        """Unsubscribe from an event type."""
        if event_type in self._listeners:
            self._listeners[event_type].remove(callback)

    def _get_websocket_manager(self):
        """Lazy load WebSocket manager to avoid circular import."""
        if self._websocket_manager is None:
            try:
                from services.websocket_manager import get_websocket_manager
                self._websocket_manager = get_websocket_manager()
            except ImportError:
                logger.warning("WebSocket manager not available")
        return self._websocket_manager

    def emit(self, event_type: str, data: Dict[str, Any]):
        """
        Emit an event to all subscribers and broadcast via WebSocket.

        Args:
            event_type: Type of event
            data: Event data
        """
        event = {
            "type": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data
        }

        logger.info(f"Emitting event: {event_type} for CI {data.get('ci_id')}")

        # Call local callbacks
        if event_type in self._listeners:
            for callback in self._listeners[event_type]:
                try:
                    callback(event)
                except Exception as e:
                    logger.error(f"Error in event callback: {str(e)}")

        # Broadcast via WebSocket
        ws_manager = self._get_websocket_manager()
        if ws_manager:
            try:
                asyncio.create_task(self._broadcast_event(event_type, data))
            except RuntimeError:
                # Not in async context, skip WebSocket broadcast
                logger.debug("Skipping WebSocket broadcast (not in async context)")

    def emit_activity_started(self, ci_id: int, activity_id: str, activity_name: str):
        """Emit activity started event."""
        self.emit("activity_started", {
            "ci_id": ci_id,
            "activity_id": activity_id,
            "activity_name": activity_name
        })

    def emit_activity_completed(
        self,
        ci_id: int,
        activity_id: str,
        activity_name: str,
        progress_percent: float
    ):
        """Emit activity completed event."""
        self.emit("activity_completed", {
            "ci_id": ci_id,
            "activity_id": activity_id,
            "activity_name": activity_name,
            "progress_percent": progress_percent
        })

    def emit_phase_completed(
        self,
        ci_id: int,
        phase_id: str,
        phase_name: str,
        progress_percent: float
    ):
        """Emit phase completed event."""
        self.emit("phase_completed", {
            "ci_id": ci_id,
            "phase_id": phase_id,
            "phase_name": phase_name,
            "progress_percent": progress_percent
        })

    def emit_progress_updated(self, ci_id: int, progress_percent: float):
        """Emit progress update event."""
        self.emit("progress_updated", {
            "ci_id": ci_id,
            "progress_percent": progress_percent
        })

    async def _broadcast_event(self, event_type: str, data: Dict[str, Any]):
        """
        Broadcast event via WebSocket.

        Args:
            event_type: Type of event
            data: Event data containing ci_id
        """
        ws_manager = self._get_websocket_manager()
        if not ws_manager:
            return

        ci_id = data.get('ci_id')
        if not ci_id:
            return

        if event_type == "activity_completed":
            await ws_manager.broadcast_activity_completed(
                ci_id=ci_id,
                activity_id=data.get('activity_id', ''),
                activity_name=data.get('activity_name', ''),
                progress_percent=data.get('progress_percent', 0.0)
            )
        elif event_type == "activity_started":
            await ws_manager.broadcast_activity_started(
                ci_id=ci_id,
                activity_id=data.get('activity_id', ''),
                activity_name=data.get('activity_name', '')
            )
        elif event_type == "phase_completed":
            await ws_manager.broadcast_phase_completed(
                ci_id=ci_id,
                phase_id=data.get('phase_id', ''),
                phase_name=data.get('phase_name', ''),
                progress_percent=data.get('progress_percent', 0.0)
            )
        elif event_type == "progress_updated":
            await ws_manager.broadcast_progress_updated(
                ci_id=ci_id,
                progress_percent=data.get('progress_percent', 0.0)
            )


# Global instance
_event_service = ProcessEventService()


def get_event_service() -> ProcessEventService:
    """Get global event service instance."""
    return _event_service
