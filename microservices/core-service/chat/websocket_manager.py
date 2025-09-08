"""
WebSocket Manager para Chat en Tiempo Real
"""

from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List, Set
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ChatWebSocketManager:
    """Manager para conexiones WebSocket del chat"""
    
    def __init__(self):
        # Conexiones por sala: {sala_id: {user_id: [websockets]}}
        self.room_connections: Dict[int, Dict[int, Set[WebSocket]]] = {}
        
        # Conexiones por usuario: {user_id: [websockets]}
        self.user_connections: Dict[int, Set[WebSocket]] = {}
        
        # Metadatos de conexiones
        self.connection_metadata: Dict[WebSocket, dict] = {}
        
        # Usuarios escribiendo por sala: {sala_id: {user_id: timestamp}}
        self.typing_users: Dict[int, Dict[int, datetime]] = {}
    
    async def connect_to_room(self, websocket: WebSocket, user_id: int, room_id: int, user_name: str = None):
        """Conectar usuario a una sala de chat"""
        await websocket.accept()
        
        # Inicializar estructuras si no existen
        if room_id not in self.room_connections:
            self.room_connections[room_id] = {}
        if user_id not in self.room_connections[room_id]:
            self.room_connections[room_id][user_id] = set()
        if user_id not in self.user_connections:
            self.user_connections[user_id] = set()
        
        # Agregar conexión
        self.room_connections[room_id][user_id].add(websocket)
        self.user_connections[user_id].add(websocket)
        
        # Guardar metadatos
        self.connection_metadata[websocket] = {
            "user_id": user_id,
            "room_id": room_id,
            "user_name": user_name or f"Usuario {user_id}",
            "connected_at": datetime.now(),
            "last_ping": datetime.now()
        }
        
        logger.info(f"💬 Usuario {user_id} conectado a sala {room_id}")
        
        # Notificar a otros usuarios de la sala que alguien se conectó
        await self.broadcast_to_room(room_id, {
            "type": "user_joined",
            "data": {
                "user_id": user_id,
                "user_name": user_name or f"Usuario {user_id}",
                "timestamp": datetime.now().isoformat()
            }
        }, exclude_user=user_id)
        
        # Enviar mensaje de bienvenida
        await self.send_to_user({
            "type": "room_joined",
            "data": {
                "room_id": room_id,
                "message": f"Te has unido a la sala de chat",
                "connected_users": self.get_room_users(room_id)
            }
        }, user_id, websocket)
    
    async def disconnect(self, websocket: WebSocket):
        """Desconectar WebSocket"""
        metadata = self.connection_metadata.get(websocket, {})
        user_id = metadata.get("user_id")
        room_id = metadata.get("room_id")
        user_name = metadata.get("user_name")
        
        if user_id and room_id:
            # Remover de sala
            if (room_id in self.room_connections and 
                user_id in self.room_connections[room_id]):
                self.room_connections[room_id][user_id].discard(websocket)
                
                # Si no hay más conexiones del usuario en esta sala
                if not self.room_connections[room_id][user_id]:
                    del self.room_connections[room_id][user_id]
                    
                    # Notificar que el usuario se desconectó
                    try:
                        await self.broadcast_to_room(room_id, {
                            "type": "user_left",
                            "data": {
                                "user_id": user_id,
                                "user_name": user_name,
                                "timestamp": datetime.now().isoformat()
                            }
                        }, exclude_user=user_id)
                    except Exception as e:
                        logger.error(f"Error notificando desconexión: {e}")
                
                # Si la sala queda vacía
                if not self.room_connections[room_id]:
                    del self.room_connections[room_id]
        
        # Remover de conexiones de usuario
        if user_id and user_id in self.user_connections:
            self.user_connections[user_id].discard(websocket)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]
        
        # Limpiar metadatos
        if websocket in self.connection_metadata:
            del self.connection_metadata[websocket]
        
        # Limpiar estado de escritura
        if room_id and room_id in self.typing_users and user_id in self.typing_users[room_id]:
            del self.typing_users[room_id][user_id]
        
        logger.info(f"💬 Usuario {user_id} desconectado de sala {room_id}")
    
    async def send_to_user(self, message: dict, user_id: int, specific_websocket: WebSocket = None):
        """Enviar mensaje a un usuario específico"""
        if specific_websocket:
            try:
                await specific_websocket.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"❌ Error enviando mensaje a WebSocket específico: {e}")
                self.disconnect(specific_websocket)
        elif user_id in self.user_connections:
            disconnected = set()
            for websocket in self.user_connections[user_id]:
                try:
                    await websocket.send_text(json.dumps(message))
                except Exception as e:
                    logger.error(f"❌ Error enviando a usuario {user_id}: {e}")
                    disconnected.add(websocket)
            
            # Limpiar conexiones muertas
            for ws in disconnected:
                self.disconnect(ws)
    
    async def broadcast_to_room(self, room_id: int, message: dict, exclude_user: int = None):
        """Enviar mensaje a todos los usuarios de una sala"""
        if room_id not in self.room_connections:
            return
        
        disconnected = set()
        for user_id, websockets in self.room_connections[room_id].items():
            if exclude_user and user_id == exclude_user:
                continue
                
            for websocket in websockets:
                try:
                    await websocket.send_text(json.dumps(message))
                except Exception as e:
                    logger.error(f"❌ Error enviando a sala {room_id}, usuario {user_id}: {e}")
                    disconnected.add(websocket)
        
        # Limpiar conexiones muertas
        for ws in disconnected:
            self.disconnect(ws)
    
    async def handle_typing_status(self, user_id: int, room_id: int, is_typing: bool):
        """Manejar estado de escritura"""
        if room_id not in self.typing_users:
            self.typing_users[room_id] = {}
        
        if is_typing:
            self.typing_users[room_id][user_id] = datetime.now()
        elif user_id in self.typing_users[room_id]:
            del self.typing_users[room_id][user_id]
        
        # Notificar a otros usuarios
        await self.broadcast_to_room(room_id, {
            "type": "typing_status",
            "data": {
                "user_id": user_id,
                "is_typing": is_typing,
                "room_id": room_id
            }
        }, exclude_user=user_id)
    
    def get_room_users(self, room_id: int) -> List[dict]:
        """Obtener lista de usuarios conectados en una sala"""
        if room_id not in self.room_connections:
            return []
        
        users = []
        for user_id in self.room_connections[room_id]:
            metadata = None
            # Buscar metadatos de alguna conexión del usuario
            for websocket in self.room_connections[room_id][user_id]:
                if websocket in self.connection_metadata:
                    metadata = self.connection_metadata[websocket]
                    break
            
            users.append({
                "user_id": user_id,
                "user_name": metadata.get("user_name", f"Usuario {user_id}") if metadata else f"Usuario {user_id}",
                "connected_at": metadata.get("connected_at").isoformat() if metadata else None
            })
        
        return users
    
    def get_stats(self) -> dict:
        """Obtener estadísticas de conexiones"""
        total_connections = sum(
            len(user_connections) 
            for room_connections in self.room_connections.values()
            for user_connections in room_connections.values()
        )
        
        return {
            "total_rooms": len(self.room_connections),
            "total_connections": total_connections,
            "total_users": len(self.user_connections),
            "rooms_with_users": {
                room_id: len(users) 
                for room_id, users in self.room_connections.items()
            }
        }

# Instancia global del manager
chat_manager = ChatWebSocketManager()
