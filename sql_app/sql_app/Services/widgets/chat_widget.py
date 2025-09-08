"""
Chat Widget - Clase Python para el widget de chat
"""

from typing import Dict, Any, Optional, List
from fastapi import Request


class ChatWidget:
    """Widget de chat para integración en páginas web"""
    
    def __init__(self, 
                 widget_id: str = "chat-widget",
                 ws_url: str = "/chat/ws/room/",
                 api_url: str = "/chat/api/",
                 room_id: int = 1,
                 user_id: Optional[int] = None,
                 user_name: str = "Usuario",
                 position: str = "bottom-right",
                 show_user_list: bool = True,
                 max_messages: int = 100,
                 auto_connect: bool = True):
        
        self.widget_id = widget_id
        self.ws_url = ws_url
        self.api_url = api_url
        self.room_id = room_id
        self.user_id = user_id
        self.user_name = user_name
        self.position = position
        self.show_user_list = show_user_list
        self.max_messages = max_messages
        self.auto_connect = auto_connect
    
    def get_config(self) -> Dict[str, Any]:
        """Obtener configuración del widget"""
        return {
            "widget_id": self.widget_id,
            "ws_url": self.ws_url,
            "api_url": self.api_url,
            "room_id": self.room_id,
            "user_id": self.user_id,
            "user_name": self.user_name,
            "position": self.position,
            "show_user_list": self.show_user_list,
            "max_messages": self.max_messages,
            "auto_connect": self.auto_connect,
            "type": "chat_widget"
        }
    
    def get_html(self, container_id: Optional[str] = None) -> str:
        """Generar HTML del contenedor del widget"""
        container_id = container_id or self.widget_id
        
        return f'''
        <div id="{container_id}" class="chat-widget-container"></div>
        '''
    
    def get_init_script(self, container_id: Optional[str] = None, options: Optional[Dict] = None) -> str:
        """Generar script de inicialización del widget"""
        container_id = container_id or self.widget_id
        widget_options = self.get_config()
        
        if options:
            widget_options.update(options)
        
        options_json = str(widget_options).replace("'", '"').replace("True", "true").replace("False", "false").replace("None", "null")
        
        return f'''
        <script>
        document.addEventListener('DOMContentLoaded', function() {{
            if (typeof loadChatWidget !== 'undefined') {{
                loadChatWidget('{container_id}', {options_json})
                    .then(widget => {{
                        console.log('Chat widget loaded successfully');
                        window.chatWidget_{container_id.replace("-", "_")} = widget;
                    }})
                    .catch(error => {{
                        console.error('Error loading chat widget:', error);
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
    def create_floating_widget(cls, 
                             container_id: str = "floating-chat",
                             room_id: int = 1,
                             position: str = "bottom-right") -> "ChatWidget":
        """Crear widget de chat flotante"""
        return cls(
            widget_id=container_id,
            room_id=room_id,
            position=position,
            auto_connect=True,
            show_user_list=True
        )
    
    @classmethod
    def create_embedded_widget(cls,
                             container_id: str = "embedded-chat",
                             room_id: int = 1) -> "ChatWidget":
        """Crear widget de chat embebido"""
        return cls(
            widget_id=container_id,
            room_id=room_id,
            position="relative",
            auto_connect=True,
            show_user_list=True
        )
    
    @classmethod
    def create_support_widget(cls,
                            container_id: str = "support-chat",
                            user_name: str = "Cliente") -> "ChatWidget":
        """Crear widget de chat para soporte"""
        return cls(
            widget_id=container_id,
            room_id=999,  # Sala especial para soporte
            user_name=user_name,
            position="bottom-right",
            auto_connect=False,  # Conectar solo cuando se abra
            show_user_list=False
        )
    
    @classmethod
    def create_team_widget(cls,
                         container_id: str = "team-chat",
                         room_id: int = 1,
                         user_name: str = "Team Member") -> "ChatWidget":
        """Crear widget de chat para equipos"""
        return cls(
            widget_id=container_id,
            room_id=room_id,
            user_name=user_name,
            position="bottom-right",
            auto_connect=True,
            show_user_list=True,
            max_messages=200
        )
