"""
Router WebSocket para Chat en Tiempo Real
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from typing import Optional
import json
import logging
from datetime import datetime

from .websocket_manager import chat_manager
from .schemas import ChatWebSocketMessage

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/chat/ws",
    tags=["chat-websocket"]
)

@router.websocket("/room/{room_id}")
async def websocket_chat_room(
    websocket: WebSocket,
    room_id: int,
    user_id: Optional[int] = Query(None, description="ID del usuario"),
    user_name: Optional[str] = Query(None, description="Nombre del usuario"),
    token: Optional[str] = Query(None, description="Token de autenticación")
):
    """
    WebSocket endpoint para chat en tiempo real por sala
    
    Parámetros:
    - room_id: ID de la sala de chat
    - user_id: ID del usuario (requerido)
    - user_name: Nombre del usuario (opcional)
    - token: Token de autenticación (opcional para demo)
    """
    
    # Validación básica
    if not user_id:
        await websocket.close(code=1008, reason="user_id requerido")
        return
    
    # Usuario por defecto para demo
    if not user_name:
        user_name = f"Usuario {user_id}"
    
    try:
        # Conectar a la sala
        await chat_manager.connect_to_room(websocket, user_id, room_id, user_name)
        
        logger.info(f"💬 {user_name} ({user_id}) conectado a sala {room_id}")
        
        # Escuchar mensajes del cliente
        while True:
            try:
                # Recibir mensaje del cliente
                data = await websocket.receive_text()
                message = json.loads(data)
                
                await handle_chat_message(message, user_id, room_id, user_name)
                
            except WebSocketDisconnect:
                break
            except json.JSONDecodeError:
                await chat_manager.send_to_user({
                    "type": "error",
                    "data": {"message": "Formato JSON inválido"}
                }, user_id, websocket)
            except Exception as e:
                logger.error(f"❌ Error procesando mensaje de chat: {e}")
                await chat_manager.send_to_user({
                    "type": "error",
                    "data": {"message": "Error interno del servidor"}
                }, user_id, websocket)
                
    except Exception as e:
        logger.error(f"❌ Error en conexión de chat: {e}")
    finally:
        chat_manager.disconnect(websocket)
        logger.info(f"💬 {user_name} desconectado de sala {room_id}")

async def handle_chat_message(message: dict, user_id: int, room_id: int, user_name: str):
    """Manejar diferentes tipos de mensajes de chat"""
    
    message_type = message.get("type")
    data = message.get("data", {})
    
    if message_type == "send_message":
        # Enviar mensaje a la sala
        content = data.get("content", "").strip()
        if content:
            chat_message = {
                "type": "new_message",
                "data": {
                    "id": int(datetime.now().timestamp() * 1000),  # ID temporal
                    "content": content,
                    "user_id": user_id,
                    "user_name": user_name,
                    "timestamp": datetime.now().isoformat(),
                    "room_id": room_id
                }
            }
            
            # Broadcast a todos en la sala
            await chat_manager.broadcast_to_room(chat_message, room_id)
            
            logger.info(f"💬 Mensaje de {user_name} en sala {room_id}: {content[:50]}...")
    
    elif message_type == "typing_start":
        # Usuario comenzó a escribir
        await chat_manager.handle_typing_status(user_id, room_id, True)
    
    elif message_type == "typing_stop":
        # Usuario dejó de escribir
        await chat_manager.handle_typing_status(user_id, room_id, False)
    
    elif message_type == "ping":
        # Ping para mantener conexión viva
        await chat_manager.send_to_user({
            "type": "pong",
            "data": {"timestamp": message.get("timestamp")}
        }, user_id)
    
    elif message_type == "get_room_users":
        # Solicitar usuarios conectados en la sala
        users = chat_manager.get_room_users(room_id)
        await chat_manager.send_to_user({
            "type": "room_users",
            "data": {"users": users, "room_id": room_id}
        }, user_id)
    
    elif message_type == "get_stats":
        # Solicitar estadísticas
        stats = chat_manager.get_stats()
        await chat_manager.send_to_user({
            "type": "chat_stats",
            "data": stats
        }, user_id)
    
    else:
        logger.warning(f"⚠️ Tipo de mensaje no manejado: {message_type}")

@router.get("/stats")
async def get_chat_stats():
    """Obtener estadísticas del chat"""
    return chat_manager.get_stats()

@router.get("/rooms/{room_id}/users")
async def get_room_users(room_id: int):
    """Obtener usuarios conectados en una sala"""
    return {
        "room_id": room_id,
        "users": chat_manager.get_room_users(room_id),
        "total": len(chat_manager.get_room_users(room_id))
    }

# Funciones auxiliares para integrar con otros módulos

async def send_system_message_to_room(room_id: int, message: str, message_type: str = "system"):
    """Enviar mensaje del sistema a una sala"""
    system_message = {
        "type": "system_message",
        "data": {
            "content": message,
            "message_type": message_type,
            "timestamp": datetime.now().isoformat(),
            "room_id": room_id
        }
    }
    
    await chat_manager.broadcast_to_room(system_message, room_id)
    logger.info(f"📢 Mensaje del sistema enviado a sala {room_id}: {message}")

async def notify_user_joined_room(room_id: int, user_id: int, user_name: str):
    """Notificar que un usuario se unió a la sala"""
    await send_system_message_to_room(
        room_id, 
        f"{user_name} se ha unido al chat", 
        "user_join"
    )

async def notify_user_left_room(room_id: int, user_id: int, user_name: str):
    """Notificar que un usuario dejó la sala"""
    await send_system_message_to_room(
        room_id, 
        f"{user_name} ha dejado el chat", 
        "user_leave"
    )
