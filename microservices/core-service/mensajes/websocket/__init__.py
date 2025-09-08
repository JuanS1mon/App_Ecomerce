"""
Módulo WebSocket para notificaciones en tiempo real
"""

from .connection_manager import connection_manager
from .router import (
    router as websocket_router,
    notify_new_message,
    notify_message_updated,
    notify_message_read,
    notify_urgent_message,
    send_system_notification
)

__all__ = [
    "connection_manager",
    "websocket_router",
    "notify_new_message",
    "notify_message_updated", 
    "notify_message_read",
    "notify_urgent_message",
    "send_system_notification"
]
