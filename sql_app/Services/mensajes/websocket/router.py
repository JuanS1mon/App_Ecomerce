"""
Router WebSocket para notificaciones de mensajes en tiempo real
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import json
import logging
from typing import Optional

from sql_app.db.database import get_db
from sql_app.db.models.config.usuarios import Usuarios
from .connection_manager import connection_manager
from ..schema_mensajes import NotificacionMensaje

logger = logging.getLogger(__name__)
security = HTTPBearer()

router = APIRouter(
    prefix="/ws",
    tags=["websocket-mensajes"]
)

async def get_user_from_token(token: Optional[str] = None) -> Optional[dict]:
    """Validar token y obtener usuario (simplificado para demo)"""
    if not token:
        return None
    
    # TODO: Implementar validación real de JWT
    # Por ahora, simulamos un usuario válido
    try:
        if token == "admin-token":
            return {"id": 1, "username": "admin", "is_admin": True}
        elif token == "user-token":
            return {"id": 2, "username": "usuario", "is_admin": False}
        else:
            return {"id": 3, "username": "demo", "is_admin": False}
    except:
        return None

@router.websocket("/notifications")
async def websocket_notifications(
    websocket: WebSocket,
    token: Optional[str] = Query(None, description="Token de autenticación"),
    user_id: Optional[int] = Query(None, description="ID del usuario (para demo)")
):
    """
    WebSocket endpoint para notificaciones en tiempo real
    
    Parámetros:
    - token: JWT token para autenticación
    - user_id: ID del usuario (para modo demo)
    """
    
    # Validar usuario
    user = await get_user_from_token(token)
    
    # Si no hay token, usar user_id para modo demo
    if not user and user_id:
        user = {"id": user_id, "username": f"user_{user_id}", "is_admin": False}
    
    # Usuario por defecto para demo
    if not user:
        user = {"id": 999, "username": "anonymous", "is_admin": False}
    
    try:
        # Conectar usuario
        await connection_manager.connect(
            websocket, 
            user_id=user["id"], 
            is_admin=user.get("is_admin", False)
        )
        
        logger.info(f"🔔 Usuario {user['username']} ({user['id']}) conectado a notificaciones")
        
        # Enviar estadísticas de conexión
        stats = connection_manager.get_connection_stats()
        await connection_manager.send_personal_message({
            "type": "connection_stats",
            "data": stats
        }, websocket)
        
        # Mantener conexión viva
        while True:
            try:
                # Esperar mensajes del cliente
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Manejar diferentes tipos de mensajes del cliente
                if message.get("type") == "ping":
                    await connection_manager.send_personal_message({
                        "type": "pong",
                        "timestamp": message.get("timestamp")
                    }, websocket)
                
                elif message.get("type") == "get_stats":
                    stats = connection_manager.get_connection_stats()
                    await connection_manager.send_personal_message({
                        "type": "connection_stats",
                        "data": stats
                    }, websocket)
                
                elif message.get("type") == "request_notifications":
                    # Solicitar notificaciones pendientes
                    await send_pending_notifications(user["id"], websocket)
                
            except WebSocketDisconnect:
                break
            except json.JSONDecodeError:
                await connection_manager.send_personal_message({
                    "type": "error",
                    "message": "Formato JSON inválido"
                }, websocket)
            except Exception as e:
                logger.error(f"❌ Error en WebSocket: {e}")
                await connection_manager.send_personal_message({
                    "type": "error",
                    "message": "Error interno del servidor"
                }, websocket)
                
    except Exception as e:
        logger.error(f"❌ Error estableciendo conexión WebSocket: {e}")
    finally:
        connection_manager.disconnect(websocket)
        logger.info(f"🔌 Usuario {user['username']} desconectado de notificaciones")

async def send_pending_notifications(user_id: int, websocket: WebSocket):
    """Enviar notificaciones pendientes al usuario"""
    # TODO: Implementar consulta real a la base de datos
    # Por ahora enviamos notificaciones de demo
    
    demo_notifications = [
        {
            "type": "new_message",
            "title": "Mensaje No Leído",
            "content": "Tienes mensajes sin leer esperando tu atención",
            "priority": "normal",
            "count": 3
        }
    ]
    
    for notification in demo_notifications:
        await connection_manager.send_personal_message({
            "type": "notification",
            "data": notification
        }, websocket)

@router.get("/stats")
async def get_websocket_stats():
    """Obtener estadísticas de conexiones WebSocket"""
    return connection_manager.get_connection_stats()

# Funciones auxiliares para enviar notificaciones desde otros módulos

async def notify_new_message(mensaje_data: dict):
    """Notificar nuevo mensaje a usuarios relevantes"""
    notification = {
        "type": "new_message",
        "data": {
            "id": mensaje_data.get("id"),
            "title": mensaje_data.get("titulo"),
            "content": mensaje_data.get("contenido")[:100] + "..." if len(mensaje_data.get("contenido", "")) > 100 else mensaje_data.get("contenido"),
            "tipo": mensaje_data.get("tipo"),
            "prioridad": mensaje_data.get("prioridad"),
            "usuario_receptor_id": mensaje_data.get("usuario_receptor_id"),
            "timestamp": mensaje_data.get("fecha_creacion")
        }
    }
    
    # Notificar al usuario receptor
    if mensaje_data.get("usuario_receptor_id"):
        await connection_manager.send_to_user(notification, mensaje_data["usuario_receptor_id"])
    
    # Notificar a administradores
    admin_notification = {
        **notification,
        "type": "admin_new_message"
    }
    await connection_manager.send_to_admins(admin_notification)
    
    logger.info(f"📨 Notificación enviada para mensaje: {mensaje_data.get('titulo')}")

async def notify_message_updated(mensaje_data: dict):
    """Notificar mensaje actualizado"""
    notification = {
        "type": "message_updated",
        "data": {
            "id": mensaje_data.get("id"),
            "title": mensaje_data.get("titulo"),
            "action": "updated"
        }
    }
    
    # Notificar al usuario receptor
    if mensaje_data.get("usuario_receptor_id"):
        await connection_manager.send_to_user(notification, mensaje_data["usuario_receptor_id"])
    
    # Notificar a administradores
    await connection_manager.send_to_admins(notification)

async def notify_message_read(mensaje_id: int, user_id: int):
    """Notificar que un mensaje fue leído"""
    notification = {
        "type": "message_read",
        "data": {
            "id": mensaje_id,
            "user_id": user_id,
            "action": "read"
        }
    }
    
    # Notificar a administradores
    await connection_manager.send_to_admins(notification)

async def notify_urgent_message(mensaje_data: dict):
    """Notificar mensaje urgente a todos los usuarios conectados"""
    notification = {
        "type": "urgent_message",
        "data": {
            "id": mensaje_data.get("id"),
            "title": mensaje_data.get("titulo"),
            "content": mensaje_data.get("contenido"),
            "tipo": mensaje_data.get("tipo"),
            "prioridad": "urgente"
        }
    }
    
    # Broadcast a todos los usuarios conectados
    await connection_manager.broadcast_message(notification)
    
    logger.warning(f"🚨 Mensaje urgente broadcast: {mensaje_data.get('titulo')}")

async def send_system_notification(title: str, content: str, notification_type: str = "system"):
    """Enviar notificación del sistema a todos los usuarios"""
    notification = {
        "type": "system_notification",
        "data": {
            "title": title,
            "content": content,
            "notification_type": notification_type,
            "timestamp": "2025-01-21T" + "12:00:00"  # timestamp actual
        }
    }
    
    await connection_manager.broadcast_message(notification)
    logger.info(f"🔔 Notificación del sistema enviada: {title}")
