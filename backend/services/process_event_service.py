"""
Process Event Service
DO-178C Traceability: REQ-SM-001, REQ-FE-TBD (Real-time updates)

This service broadcasts process events for real-time UI updates.
Uses a simple event emitter pattern that can be upgraded to WebSocket later.

Events:
- activity_completed
- activity_started
- phase_completed
- progress_updated
"""

from typing import Dict, List, Any, Callable
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ProcessEventService:
    """
    Lightweight event service for process updates.

    This is a simple in-memory event system. For production with multiple
    workers, this should be replaced with Redis pub/sub or similar.
    """

    def __init__(self):
        self._listeners: Dict[str, List[Callable]] = {}

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

    def emit(self, event_type: str, data: Dict[str, Any]):
        """
        Emit an event to all subscribers.

        Args:
            event_type: Type of event
            data: Event data
        """
        if event_type not in self._listeners:
            return

        event = {
            "type": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data
        }

        logger.info(f"Emitting event: {event_type} for CI {data.get('ci_id')}")

        for callback in self._listeners[event_type]:
            try:
                callback(event)
            except Exception as e:
                logger.error(f"Error in event callback: {str(e)}")

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


# Global instance
_event_service = ProcessEventService()


def get_event_service() -> ProcessEventService:
    """Get global event service instance."""
    return _event_service
