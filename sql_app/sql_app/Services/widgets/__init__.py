"""
Sistema de Widgets - Chat y Mensajes
Componentes modulares y reutilizables para integrar en cualquier página
"""

from .widget_loader import WidgetLoader
from .message_widget import MessageWidget
from .chat_widget import ChatWidget

__all__ = [
    "WidgetLoader",
    "MessageWidget", 
    "ChatWidget"
]
