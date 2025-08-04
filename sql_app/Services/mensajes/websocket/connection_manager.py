"""
Módulo WebSocket para notificaciones en tiempo real de mensajes
"""

from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List, Set
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ConnectionManager:
    """Manager para conexiones WebSocket"""
    
    def __init__(self):
        # Conexiones activas por usuario
        self.active_connections: Dict[int, Set[WebSocket]] = {}
        # Conexiones globales (admins)
        self.admin_connections: Set[WebSocket] = set()
        # Metadatos de conexiones
        self.connection_metadata: Dict[WebSocket, dict] = {}
    
    async def connect(self, websocket: WebSocket, user_id: int = None, is_admin: bool = False):
        """Aceptar nueva conexión WebSocket"""
        await websocket.accept()
        
        # Almacenar metadatos de la conexión
        self.connection_metadata[websocket] = {
            "user_id": user_id,
            "is_admin": is_admin,
            "connected_at": datetime.now(),
            "last_ping": datetime.now()
        }
        
        if is_admin:
            self.admin_connections.add(websocket)
            logger.info(f"🔗 Admin conectado. Total admins: {len(self.admin_connections)}")
        
        if user_id:
            if user_id not in self.active_connections:
                self.active_connections[user_id] = set()
            self.active_connections[user_id].add(websocket)
            logger.info(f"🔗 Usuario {user_id} conectado. Conexiones: {len(self.active_connections[user_id])}")
        
        # Enviar mensaje de bienvenida
        await self.send_personal_message({
            "type": "connection_established",
            "message": "Conectado al sistema de notificaciones",
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "is_admin": is_admin
        }, websocket)
    
    def disconnect(self, websocket: WebSocket):
        """Desconectar WebSocket"""
        metadata = self.connection_metadata.get(websocket, {})
        user_id = metadata.get("user_id")
        is_admin = metadata.get("is_admin", False)
        
        if is_admin:
            self.admin_connections.discard(websocket)
            logger.info(f"❌ Admin desconectado. Total admins: {len(self.admin_connections)}")
        
        if user_id and user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
            logger.info(f"❌ Usuario {user_id} desconectado")
        
        # Limpiar metadatos
        if websocket in self.connection_metadata:
            del self.connection_metadata[websocket]
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Enviar mensaje a una conexión específica"""
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"❌ Error enviando mensaje personal: {e}")
            self.disconnect(websocket)
    
    async def send_to_user(self, message: dict, user_id: int):
        """Enviar mensaje a todas las conexiones de un usuario"""
        if user_id in self.active_connections:
            disconnected = set()
            for websocket in self.active_connections[user_id]:
                try:
                    await websocket.send_text(json.dumps(message))
                except Exception as e:
                    logger.error(f"❌ Error enviando a usuario {user_id}: {e}")
                    disconnected.add(websocket)
            
            # Limpiar conexiones muertas
            for ws in disconnected:
                self.disconnect(ws)
    
    async def send_to_admins(self, message: dict):
        """Enviar mensaje a todos los administradores conectados"""
        disconnected = set()
        for websocket in self.admin_connections:
            try:
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"❌ Error enviando a admin: {e}")
                disconnected.add(websocket)
        
        # Limpiar conexiones muertas
        for ws in disconnected:
            self.disconnect(ws)
    
    async def broadcast_message(self, message: dict):
        """Enviar mensaje a todas las conexiones activas"""
        all_websockets = set()
        
        # Recopilar todas las conexiones
        for user_connections in self.active_connections.values():
            all_websockets.update(user_connections)
        all_websockets.update(self.admin_connections)
        
        disconnected = set()
        for websocket in all_websockets:
            try:
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"❌ Error en broadcast: {e}")
                disconnected.add(websocket)
        
        # Limpiar conexiones muertas
        for ws in disconnected:
            self.disconnect(ws)
    
    def get_connection_stats(self) -> dict:
        """Obtener estadísticas de conexiones"""
        total_user_connections = sum(len(connections) for connections in self.active_connections.values())
        
        return {
            "total_users_connected": len(self.active_connections),
            "total_user_connections": total_user_connections,
            "total_admin_connections": len(self.admin_connections),
            "total_connections": total_user_connections + len(self.admin_connections),
            "users_online": list(self.active_connections.keys())
        }
    
    async def ping_all_connections(self):
        """Enviar ping a todas las conexiones para mantenerlas vivas"""
        ping_message = {
            "type": "ping",
            "timestamp": datetime.now().isoformat()
        }
        await self.broadcast_message(ping_message)

# Instancia global del manager
connection_manager = ConnectionManager()
