"""
Message Widget - Clase Python para el widget de mensajes
"""

from typing import Dict, Any, Optional, List
from fastapi import Request
from sqlalchemy.orm import Session


class MessageWidget:
    """Widget de mensajes para integración en páginas web"""
    
    def __init__(self, 
                 widget_id: str = "message-widget",
                 api_url: str = "/api/mensajes/",
                 ws_url: str = "/ws/notifications",
                 max_messages: int = 10,
                 auto_refresh: bool = True,
                 position: str = "top-right"):
        
        self.widget_id = widget_id
        self.api_url = api_url
        self.ws_url = ws_url
        self.max_messages = max_messages
        self.auto_refresh = auto_refresh
        self.position = position
    
    def get_config(self) -> Dict[str, Any]:
        """Obtener configuración del widget"""
        return {
            "widget_id": self.widget_id,
            "api_url": self.api_url,
            "ws_url": self.ws_url,
            "max_messages": self.max_messages,
            "auto_refresh": self.auto_refresh,
            "position": self.position,
            "type": "message_widget"
        }
    
    def get_html(self, container_id: Optional[str] = None) -> str:
        """Generar HTML del contenedor del widget"""
        container_id = container_id or self.widget_id
        
        return f'''
        <div id="{container_id}" class="message-widget-container"></div>
        '''
    
    def get_init_script(self, container_id: Optional[str] = None, options: Optional[Dict] = None) -> str:
        """Generar script de inicialización del widget"""
        container_id = container_id or self.widget_id
        widget_options = self.get_config()
        
        if options:
            widget_options.update(options)
        
        options_json = str(widget_options).replace("'", '"').replace("True", "true").replace("False", "false")
        
        return f'''
        <script>
        document.addEventListener('DOMContentLoaded', function() {{
            if (typeof loadMessageWidget !== 'undefined') {{
                loadMessageWidget('{container_id}', {options_json})
                    .then(widget => {{
                        console.log('Message widget loaded successfully');
                        window.messageWidget_{container_id.replace("-", "_")} = widget;
                    }})
                    .catch(error => {{
                        console.error('Error loading message widget:', error);
                    }});
            }} else {{
                console.error('WidgetLoader not found. Include /widgets/loader.js first.');
            }}
        }});
        </script>
        '''
    
    def render_full(self, 
                   container_id: Optional[str] = None, 
                   options: Optional[Dict] = None,
                   include_loader: bool = True) -> str:
        """Renderizar widget completo con loader"""
        
        loader_script = '''
        <script src="/widgets/loader.js"></script>
        ''' if include_loader else ''
        
        html = self.get_html(container_id)
        script = self.get_init_script(container_id, options)
        
        return f'{loader_script}{html}{script}'
    
    @classmethod
    def create_navbar_widget(cls, 
                           container_id: str = "navbar-messages",
                           position: str = "top-right") -> "MessageWidget":
        """Crear widget optimizado para navbar"""
        return cls(
            widget_id=container_id,
            position=position,
            max_messages=5,
            auto_refresh=True
        )
    
    @classmethod
    def create_sidebar_widget(cls,
                            container_id: str = "sidebar-messages") -> "MessageWidget":
        """Crear widget optimizado para sidebar"""
        return cls(
            widget_id=container_id,
            position="relative",
            max_messages=15,
            auto_refresh=True
        )
    
    @classmethod
    def create_dashboard_widget(cls,
                              container_id: str = "dashboard-messages") -> "MessageWidget":
        """Crear widget optimizado para dashboard"""
        return cls(
            widget_id=container_id,
            position="relative",
            max_messages=20,
            auto_refresh=True
        )
