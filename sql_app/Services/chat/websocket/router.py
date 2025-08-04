"""
Router WebSocket para Chat Global
Sistema de comunicación en tiempo real para chat entre usuarios
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Depends, Query
from typing import Dict, Set, List
import json
import asyncio
import logging
from datetime import datetime
from sql_app.Services.chat.websocket_manager import ChatWebSocketManager
from sql_app.Services.chat.models import ChatRoom, ChatMessage
from sql_app.Services.chat.schemas import ChatRoomCreate, ChatMessageCreate
from sql_app.db.database import get_db
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

# Router para WebSocket
router = APIRouter()

# Manager global de conexiones WebSocket
chat_manager = ChatWebSocketManager()

@router.websocket("/ws/room/{room_id}")
async def websocket_chat_endpoint(
    websocket: WebSocket,
    room_id: int,
    user_id: int = Query(..., description="ID del usuario"),
    user_name: str = Query("Usuario Anónimo", description="Nombre del usuario")
):
    """
    Endpoint WebSocket para conexión al chat de una sala específica
    
    Parámetros:
    - room_id: ID de la sala de chat
    - user_id: ID del usuario conectándose
    - user_name: Nombre del usuario para mostrar
    """
    
    logger.info(f"💬 Nueva conexión WebSocket - Sala: {room_id}, Usuario: {user_name} ({user_id})")
    
    try:
        # Aceptar conexión WebSocket
        await websocket.accept()
        
        # Agregar conexión al manager
        await chat_manager.connect(websocket, room_id, user_id, user_name)
        
        # Notificar a otros usuarios que alguien se unió
        await chat_manager.broadcast_to_room(room_id, {
            "type": "user_joined",
            "data": {
                "user_id": user_id,
                "user_name": user_name,
                "timestamp": datetime.now().isoformat()
            }
        }, exclude_user=user_id)
        
        # Enviar lista de usuarios conectados al usuario que se conectó
        connected_users = chat_manager.get_room_users(room_id)
        await websocket.send_text(json.dumps({
            "type": "room_users",
            "data": {
                "users": [
                    {
                        "user_id": uid,
                        "user_name": uname,
                        "connected_at": conn_time.isoformat()
                    }
                    for uid, uname, conn_time in connected_users
                ]
            }
        }))
        
        # Bucle principal para manejar mensajes
        while True:
            try:
                # Recibir mensaje del cliente
                data = await websocket.receive_text()
                message_data = json.loads(data)
                
                logger.debug(f"📨 Mensaje recibido: {message_data}")
                
                # Procesar mensaje según su tipo
                await process_chat_message(
                    websocket=websocket,
                    room_id=room_id,
                    user_id=user_id,
                    user_name=user_name,
                    message_data=message_data
                )
                
            except WebSocketDisconnect:
                logger.info(f"🔌 Usuario {user_name} ({user_id}) desconectado de sala {room_id}")
                break
            except json.JSONDecodeError:
                logger.warning(f"⚠️ Mensaje JSON inválido de usuario {user_id}")
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "data": {"message": "Formato de mensaje inválido"}
                }))
            except Exception as e:
                logger.error(f"❌ Error procesando mensaje: {e}")
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "data": {"message": "Error interno del servidor"}
                }))
                
    except Exception as e:
        logger.error(f"❌ Error en conexión WebSocket: {e}")
    finally:
        # Limpiar conexión
        await chat_manager.disconnect(websocket)
        
        # Notificar a otros usuarios que alguien se fue
        await chat_manager.broadcast_to_room(room_id, {
            "type": "user_left",
            "data": {
                "user_id": user_id,
                "user_name": user_name,
                "timestamp": datetime.now().isoformat()
            }
        }, exclude_user=user_id)


async def process_chat_message(
    websocket: WebSocket,
    room_id: int,
    user_id: int,
    user_name: str,
    message_data: dict
):
    """
    Procesar diferentes tipos de mensajes del chat
    """
    
    message_type = message_data.get("type")
    data = message_data.get("data", {})
    
    try:
        if message_type == "send_message":
            # Enviar mensaje de chat
            content = data.get("content", "").strip()
            if not content:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "data": {"message": "El mensaje no puede estar vacío"}
                }))
                return
            
            # Crear mensaje en el chat
            chat_message = {
                "type": "new_message",
                "data": {
                    "room_id": room_id,
                    "user_id": user_id,
                    "user_name": user_name,
                    "content": content,
                    "timestamp": datetime.now().isoformat(),
                    "message_id": f"{user_id}_{int(datetime.now().timestamp())}"
                }
            }
            
            # Broadcast del mensaje a todos en la sala
            await chat_manager.broadcast_to_room(room_id, chat_message)
            
            logger.info(f"💬 Mensaje enviado en sala {room_id}: {user_name}: {content[:50]}...")
            
        elif message_type == "typing_start":
            # Usuario empezó a escribir
            await chat_manager.broadcast_to_room(room_id, {
                "type": "typing_status",
                "data": {
                    "user_id": user_id,
                    "user_name": user_name,
                    "is_typing": True,
                    "timestamp": datetime.now().isoformat()
                }
            }, exclude_user=user_id)
            
            # Marcar usuario como escribiendo
            chat_manager.set_typing_status(room_id, user_id, True)
            
        elif message_type == "typing_stop":
            # Usuario dejó de escribir
            await chat_manager.broadcast_to_room(room_id, {
                "type": "typing_status",
                "data": {
                    "user_id": user_id,
                    "user_name": user_name,
                    "is_typing": False,
                    "timestamp": datetime.now().isoformat()
                }
            }, exclude_user=user_id)
            
            # Desmarcar usuario como escribiendo
            chat_manager.set_typing_status(room_id, user_id, False)
            
        elif message_type == "ping":
            # Responder a ping con pong
            await websocket.send_text(json.dumps({
                "type": "pong",
                "data": {
                    "timestamp": datetime.now().isoformat(),
                    "server_time": datetime.now().timestamp()
                }
            }))
            
        elif message_type == "get_room_users":
            # Solicitar lista de usuarios conectados
            connected_users = chat_manager.get_room_users(room_id)
            await websocket.send_text(json.dumps({
                "type": "room_users",
                "data": {
                    "users": [
                        {
                            "user_id": uid,
                            "user_name": uname,
                            "connected_at": conn_time.isoformat()
                        }
                        for uid, uname, conn_time in connected_users
                    ]
                }
            }))
            
        elif message_type == "get_stats":
            # Obtener estadísticas del chat
            stats = chat_manager.get_chat_stats()
            await websocket.send_text(json.dumps({
                "type": "chat_stats",
                "data": stats
            }))
            
        else:
            # Tipo de mensaje no reconocido
            await websocket.send_text(json.dumps({
                "type": "error",
                "data": {"message": f"Tipo de mensaje no reconocido: {message_type}"}
            }))
            
    except Exception as e:
        logger.error(f"❌ Error procesando mensaje tipo '{message_type}': {e}")
        await websocket.send_text(json.dumps({
            "type": "error",
            "data": {"message": "Error procesando mensaje"}
        }))


# Endpoints HTTP adicionales para el chat
@router.get("/rooms/{room_id}/users")
async def get_room_users_http(room_id: int):
    """
    Obtener lista de usuarios conectados a una sala (vía HTTP)
    """
    try:
        connected_users = chat_manager.get_room_users(room_id)
        return {
            "room_id": room_id,
            "users_count": len(connected_users),
            "users": [
                {
                    "user_id": uid,
                    "user_name": uname,
                    "connected_at": conn_time.isoformat()
                }
                for uid, uname, conn_time in connected_users
            ]
        }
    except Exception as e:
        logger.error(f"❌ Error obteniendo usuarios de sala {room_id}: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.get("/stats")
async def get_chat_stats_http():
    """
    Obtener estadísticas generales del chat (vía HTTP)
    """
    try:
        stats = chat_manager.get_chat_stats()
        return {
            "status": "active",
            "timestamp": datetime.now().isoformat(),
            **stats
        }
    except Exception as e:
        logger.error(f"❌ Error obteniendo estadísticas del chat: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.post("/rooms/{room_id}/broadcast")
async def broadcast_message_http(
    room_id: int,
    message: dict,
    admin_key: str = None
):
    """
    Enviar mensaje broadcast a una sala (vía HTTP, para administradores)
    """
    try:
        # Verificación básica de admin (en producción usar autenticación real)
        if admin_key != "admin_broadcast_key_123":
            raise HTTPException(status_code=403, detail="No autorizado")
        
        # Crear mensaje del sistema
        system_message = {
            "type": "system_message",
            "data": {
                "content": message.get("content", "Mensaje del sistema"),
                "timestamp": datetime.now().isoformat(),
                "sender": "Sistema"
            }
        }
        
        # Enviar a todos en la sala
        await chat_manager.broadcast_to_room(room_id, system_message)
        
        return {
            "status": "sent",
            "room_id": room_id,
            "message": message.get("content"),
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error enviando broadcast a sala {room_id}: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


# Endpoint de prueba para el chat
@router.get("/test")
async def test_chat_endpoint():
    """
    Endpoint de prueba para verificar que el sistema de chat está funcionando
    """
    stats = chat_manager.get_chat_stats()
    return {
        "status": "Chat system operational",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "websocket_endpoint": "/chat/ws/room/{room_id}",
        "current_stats": stats,
        "test_room": {
            "room_id": 1,
            "connect_url": "ws://localhost:8000/chat/ws/room/1?user_id=999&user_name=Test User"
        }
    }


# Endpoint para servir la página de pruebas
@router.get("/test-page")
async def serve_test_page():
    """
    Servir la página HTML de pruebas del sistema de chat
    """
    from fastapi.responses import FileResponse
    import os
    
    # Ruta al archivo HTML de pruebas
    test_file_path = os.path.join(
        os.path.dirname(__file__), 
        "..", 
        "test_chat_system.html"
    )
    
    # Verificar que el archivo existe
    if os.path.exists(test_file_path):
        return FileResponse(
            path=test_file_path,
            media_type="text/html",
            filename="test_chat_system.html"
        )
    else:
        raise HTTPException(
            status_code=404, 
            detail="Página de pruebas no encontrada"
        )
