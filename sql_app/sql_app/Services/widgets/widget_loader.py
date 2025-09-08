"""
Widget Loader - Sistema de carga dinámica de widgets
Permite cargar widgets de chat y mensajes en cualquier página
"""

from fastapi import APIRouter, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.templating import Jinja2Templates
import os
from typing import Dict, Any

router = APIRouter(
    prefix="/widgets",
    tags=["widgets"]
)

class WidgetLoader:
    """Cargador de widgets dinámico"""
    
    def __init__(self):
        self.widget_path = "sql_app/Services/widgets/templates"
        self.static_path = "sql_app/Services/widgets/static"
    
    def get_widget_config(self, widget_type: str) -> Dict[str, Any]:
        """Obtener configuración de un widget específico"""
        configs = {
            "messages": {
                "name": "Widget de Mensajes",
                "description": "Notificaciones y contador de mensajes",
                "css": ["/widgets/static/css/message-widget.css"],
                "js": ["/widgets/static/js/message-widget.js"],
                "websocket": "/ws/notifications",
                "api": "/api/public/mensajes/",
                "dependencies": ["font-awesome"]
            },
            "chat": {
                "name": "Widget de Chat",
                "description": "Chat en tiempo real flotante",
                "css": ["/widgets/static/css/chat-widget.css"],
                "js": ["/widgets/static/js/chat-widget.js"],
                "websocket": "/chat/ws/room/",
                "api": "/chat/api/",
                "dependencies": ["font-awesome"]
            }
        }
        return configs.get(widget_type, {})

# Instancia global del loader
widget_loader = WidgetLoader()

@router.get("/config/{widget_type}")
async def get_widget_config(widget_type: str):
    """Endpoint para obtener configuración de widgets"""
    config = widget_loader.get_widget_config(widget_type)
    if not config:
        return JSONResponse(
            status_code=404, 
            content={"error": f"Widget '{widget_type}' no encontrado"}
        )
    return config

@router.get("/loader.js")
async def widget_loader_script():
    """Script JavaScript para cargar widgets dinámicamente"""
    script_content = """
// Widget Loader - Sistema de carga dinámica de widgets
class WidgetLoader {
    constructor() {
        this.widgets = {};
        this.baseUrl = window.location.origin;
    }

    // Cargar widget de mensajes
    async loadMessageWidget(containerId, options = {}) {
        try {
            const config = await this.fetchWidgetConfig('messages');
            await this.loadDependencies(config.dependencies);
            await this.loadStyles(config.css);
            
            // Cargar scripts JavaScript si no están cargados
            await this.loadScripts(config.js);
            
            // Verificar que MessageWidget esté disponible
            if (typeof MessageWidget === 'undefined') {
                throw new Error('MessageWidget class not loaded after loading scripts');
            }
            
            const userInfo = this.getUserInfo();
            const widget = new MessageWidget(containerId, {
                apiUrl: config.api,
                wsUrl: config.websocket,
                userId: userInfo.id,
                userName: userInfo.name,
                ...options
            });
            
            this.widgets[containerId] = widget;
            await widget.init();
            return widget;
        } catch (error) {
            console.error('Error loading message widget:', error);
            throw error;
        }
    }

    // Cargar widget de chat
    async loadChatWidget(containerId, options = {}) {
        try {
            const config = await this.fetchWidgetConfig('chat');
            await this.loadDependencies(config.dependencies);
            await this.loadStyles(config.css);
            
            // Cargar scripts JavaScript si no están cargados
            await this.loadScripts(config.js);
            
            // Verificar que ChatWidget esté disponible
            if (typeof ChatWidget === 'undefined') {
                throw new Error('ChatWidget class not loaded after loading scripts');
            }
            
            const userInfo = this.getUserInfo();
            console.log('🚀 Inicializando ChatWidget con configuración:', {
                userId: userInfo.id,
                userName: userInfo.name,
                wsUrl: config.websocket,
                apiUrl: config.api,
                roomId: 1
            });
            
            const widget = new ChatWidget(containerId, {
                apiUrl: config.api,
                wsUrl: config.websocket,
                roomId: 1, // Sala por defecto
                userId: userInfo.id,
                userName: userInfo.name,
                displayName: userInfo.display_name,
                autoConnect: true,
                ...options
            });
            
            this.widgets[containerId] = widget;
            await widget.init();
            return widget;
        } catch (error) {
            console.error('❌ Error al cargar widget de chat:', error);
            throw error;
        }
    }

    // Obtener configuración de widget
    async fetchWidgetConfig(type) {
        const response = await fetch(`${this.baseUrl}/widgets/config/${type}`);
        if (!response.ok) {
            throw new Error(`Failed to fetch widget config: ${response.statusText}`);
        }
        return response.json();
    }

    // Cargar dependencias
    async loadDependencies(dependencies) {
        const promises = dependencies.map(dep => {
            switch(dep) {
                case 'font-awesome':
                    return this.loadCSS('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css');
                default:
                    return Promise.resolve();
            }
        });
        await Promise.all(promises);
    }

    // Cargar estilos CSS
    async loadStyles(cssFiles) {
        const promises = cssFiles.map(file => 
            this.loadCSS(this.baseUrl + file)
        );
        await Promise.all(promises);
    }

    // Cargar archivo CSS
    loadCSS(href) {
        return new Promise((resolve, reject) => {
            // Verificar si ya está cargado
            if (document.querySelector(`link[href="${href}"]`)) {
                resolve();
                return;
            }
            
            const link = document.createElement('link');
            link.rel = 'stylesheet';
            link.href = href;
            link.onload = resolve;
            link.onerror = reject;
            document.head.appendChild(link);
        });
    }

    // Cargar múltiples scripts JavaScript
    async loadScripts(jsFiles) {
        const promises = jsFiles.map(file => 
            this.loadScript(this.baseUrl + file)
        );
        await Promise.all(promises);
    }

    // Cargar script JavaScript
    loadScript(src) {
        return new Promise((resolve, reject) => {
            if (document.querySelector(`script[src="${src}"]`)) {
                resolve();
                return;
            }
            
            const script = document.createElement('script');
            script.src = src;
            script.onload = resolve;
            script.onerror = reject;
            document.head.appendChild(script);
        });
    }

    // Destruir widget
    destroyWidget(containerId) {
        if (this.widgets[containerId]) {
            if (this.widgets[containerId].destroy) {
                this.widgets[containerId].destroy();
            }
            delete this.widgets[containerId];
        }
    }

    // Generar ID de usuario único para testing
    generateUserId() {
        return Math.floor(Math.random() * 10000);
    }

    // Obtener información del usuario para testing
    getUserInfo() {
        return {
            id: this.generateUserId(),
            name: 'juan',  // Usuario de prueba
            display_name: 'Juan (Prueba)'
        };
    }
}

// Crear instancia global
window.WidgetLoader = new WidgetLoader();

// Función de conveniencia para cargar widgets
window.loadMessageWidget = (containerId, options) => 
    window.WidgetLoader.loadMessageWidget(containerId, options);

window.loadChatWidget = (containerId, options) => 
    window.WidgetLoader.loadChatWidget(containerId, options);
"""
    return Response(
        content=script_content,
        media_type="application/javascript"
    )

@router.get("/chat")
async def chat_widget_page():
    """Página de prueba del widget de chat"""
    html_content = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chat Widget - Prueba</title>
    <link rel="stylesheet" href="/widgets/static/css/chat-widget.css">
</head>
<body>
    <div style="padding: 20px;">
        <h1>Chat Widget - Página de Prueba</h1>
        <p>El widget de chat aparecerá en la esquina inferior derecha.</p>
        <div id="chat-container"></div>
    </div>
    
    <script src="/widgets/static/js/chat-widget.js"></script>
    <script>
        // Inicializar el chat widget
        document.addEventListener('DOMContentLoaded', function() {
            const chatWidget = new ChatWidget('chat-container', {
                userId: 'test-user-123',
                userName: 'Usuario de Prueba',
                roomId: 'general'
            });
            chatWidget.init();
        });
    </script>
</body>
</html>
"""
    return HTMLResponse(content=html_content)

@router.get("/demo")
async def demo_widgets_page():
    """Página demo con ambos widgets"""
    with open("sql_app/Services/widgets/demo.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

@router.get("/debug")
async def debug_chat_page():
    """Página de debug del chat widget"""
    return FileResponse("debug_chat.html")

@router.get("/test-ws")
async def test_websocket_page():
    """Página de test WebSocket simple"""
    return FileResponse("test_websocket.html")
