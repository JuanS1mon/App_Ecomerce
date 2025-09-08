# ============================================================================
# CHAT CRUD OPERATIONS
# ============================================================================
# Operaciones CRUD para el sistema de chat

from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from sql_app.db import models
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# ============================================================================
# ALMACENAMIENTO TEMPORAL EN MEMORIA PARA TESTING
# ============================================================================

# Almacén temporal de mensajes para testing
chat_messages_store = {}

# ============================================================================
# SALAS DE CHAT
# ============================================================================

def get_all_chat_rooms(db: Session) -> List[Dict[str, Any]]:
    """Obtener conversaciones directas disponibles - CHAT DIRECTO ENTRE USUARIOS"""
    try:
        # Conversación directa entre Admin y Juan (sin salas)
        conversacion_directa = [
            {
                "id": 1,
                "name": "Chat Admin ↔ Juan",
                "description": "Conversación directa entre Admin y Juan",
                "created_at": datetime.now().isoformat(),
                "is_active": True,
                "participants": ["admin", "juan"]
            }
        ]
        
        logger.info(f"Retornando conversación directa entre usuarios")
        return conversacion_directa
        
    except Exception as e:
        logger.error(f"Error obteniendo conversación: {e}")
        return []

def get_chat_room_by_id(db: Session, room_id: int) -> Optional[Dict[str, Any]]:
    """Obtener una sala de chat por ID"""
    try:
        room = db.query(models.ChatRoom).filter(models.ChatRoom.id == room_id).first()
        
        if room:
            return {
                "id": room.id,
                "name": room.name,
                "description": room.description,
                "created_at": room.created_at.isoformat() if room.created_at else None,
                "is_active": room.is_active
            }
        
        return None
    except Exception as e:
        logger.error(f"Error obteniendo sala {room_id}: {e}")
        return None

def create_chat_room(db: Session, name: str, description: str = None) -> Dict[str, Any]:
    """Crear una nueva sala de chat"""
    try:
        room = models.ChatRoom(
            name=name,
            description=description,
            created_at=datetime.now(),
            is_active=True
        )
        
        db.add(room)
        db.commit()
        db.refresh(room)
        
        return {
            "id": room.id,
            "name": room.name,
            "description": room.description,
            "created_at": room.created_at.isoformat(),
            "is_active": room.is_active
        }
    except Exception as e:
        logger.error(f"Error creando sala: {e}")
        db.rollback()
        raise

# ============================================================================
# MENSAJES DE CHAT
# ============================================================================

def get_room_messages(db: Session, room_id: int, limit: int = 50) -> List[Dict[str, Any]]:
    """Obtener mensajes de una sala específica - VERSIÓN SIMULADA"""
    try:
        # Obtener mensajes del almacén temporal
        room_messages = chat_messages_store.get(room_id, [])
        
        # Ordenar por fecha (más recientes último)
        sorted_messages = sorted(room_messages, key=lambda x: x.get('created_at', ''))
        
        # Aplicar límite
        result = sorted_messages[-limit:] if len(sorted_messages) > limit else sorted_messages
        
        logger.info(f"Retornando {len(result)} mensajes simulados para sala {room_id}")
        return result
        
    except Exception as e:
        logger.error(f"Error obteniendo mensajes de sala {room_id}: {e}")
        return []

def create_chat_message(
    db: Session, 
    room_id: int, 
    user_id: str, 
    user_name: str, 
    message: str
) -> Dict[str, Any]:
    """Crear un nuevo mensaje de chat - VERSIÓN SIMULADA"""
    try:
        # Crear ID único para el mensaje
        import uuid
        message_id = str(uuid.uuid4())[:8]
        
        # Crear mensaje
        new_message = {
            "id": message_id,
            "room_id": room_id,
            "user_id": user_id,
            "user_name": user_name,
            "message": message,
            "created_at": datetime.now().isoformat(),
            "timestamp": datetime.now().isoformat()
        }
        
        # Almacenar en memoria
        if room_id not in chat_messages_store:
            chat_messages_store[room_id] = []
        
        chat_messages_store[room_id].append(new_message)
        
        # Mantener solo los últimos 100 mensajes por sala
        if len(chat_messages_store[room_id]) > 100:
            chat_messages_store[room_id] = chat_messages_store[room_id][-100:]
        
        logger.info(f"Mensaje simulado creado en sala {room_id} por {user_name}")
        return new_message
        
    except Exception as e:
        logger.error(f"Error creando mensaje: {e}")
        raise

def get_messages_by_user(db: Session, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
    """Obtener mensajes de un usuario específico"""
    try:
        messages = db.query(models.ChatMessage).filter(
            models.ChatMessage.user_id == user_id
        ).order_by(desc(models.ChatMessage.created_at)).limit(limit).all()
        
        result = []
        for msg in messages:
            result.append({
                "id": msg.id,
                "room_id": msg.room_id,
                "user_id": msg.user_id,
                "user_name": msg.user_name,
                "message": msg.message,
                "created_at": msg.created_at.isoformat() if msg.created_at else None
            })
        
        return result
    except Exception as e:
        logger.error(f"Error obteniendo mensajes del usuario {user_id}: {e}")
        return []

# ============================================================================
# USUARIOS Y MIEMBROS
# ============================================================================

def get_users_for_chat(db: Session) -> List[Dict[str, Any]]:
    """Obtener usuarios disponibles para chat - VERSIÓN SIMULADA"""
    try:
        # Usuarios simulados para testing
        usuarios_simulados = [
            {
                "id": "admin",
                "username": "admin",
                "email": "admin@test.com",
                "is_active": True
            },
            {
                "id": "juan",
                "username": "juan",
                "email": "juan@test.com", 
                "is_active": True
            }
        ]
        
        logger.info(f"Retornando {len(usuarios_simulados)} usuarios simulados")
        return usuarios_simulados
        
    except Exception as e:
        logger.error(f"Error obteniendo usuarios: {e}")
        return []

def get_room_members(db: Session, room_id: int) -> List[Dict[str, Any]]:
    """Obtener miembros de una sala específica"""
    try:
        members = db.query(models.ChatMember).filter(
            and_(
                models.ChatMember.room_id == room_id,
                models.ChatMember.is_active == True
            )
        ).all()
        
        result = []
        for member in members:
            # Obtener información del usuario
            user = db.query(models.Users).filter(models.Users.id == member.user_id).first()
            if user:
                result.append({
                    "user_id": member.user_id,
                    "username": user.username,
                    "email": user.email,
                    "joined_at": member.joined_at.isoformat() if member.joined_at else None,
                    "is_active": member.is_active
                })
        
        return result
    except Exception as e:
        logger.error(f"Error obteniendo miembros de sala {room_id}: {e}")
        return []

def add_user_to_room(db: Session, room_id: int, user_id: int) -> Dict[str, Any]:
    """Agregar un usuario a una sala de chat"""
    try:
        # Verificar si ya es miembro
        existing_member = db.query(models.ChatMember).filter(
            and_(
                models.ChatMember.room_id == room_id,
                models.ChatMember.user_id == user_id
            )
        ).first()
        
        if existing_member:
            if not existing_member.is_active:
                existing_member.is_active = True
                existing_member.joined_at = datetime.now()
                db.commit()
            return {"message": "Usuario ya es miembro de la sala", "success": True}
        
        # Crear nuevo miembro
        member = models.ChatMember(
            room_id=room_id,
            user_id=user_id,
            joined_at=datetime.now(),
            is_active=True
        )
        
        db.add(member)
        db.commit()
        
        return {"message": "Usuario agregado a la sala correctamente", "success": True}
    except Exception as e:
        logger.error(f"Error agregando usuario {user_id} a sala {room_id}: {e}")
        db.rollback()
        raise

def remove_user_from_room(db: Session, room_id: int, user_id: int) -> Dict[str, Any]:
    """Remover un usuario de una sala de chat"""
    try:
        member = db.query(models.ChatMember).filter(
            and_(
                models.ChatMember.room_id == room_id,
                models.ChatMember.user_id == user_id
            )
        ).first()
        
        if member:
            member.is_active = False
            db.commit()
            return {"message": "Usuario removido de la sala", "success": True}
        
        return {"message": "Usuario no encontrado en la sala", "success": False}
    except Exception as e:
        logger.error(f"Error removiendo usuario {user_id} de sala {room_id}: {e}")
        db.rollback()
        raise

# ============================================================================
# ESTADÍSTICAS
# ============================================================================

def get_chat_statistics(db: Session) -> Dict[str, Any]:
    """Obtener estadísticas generales del chat"""
    try:
        total_rooms = db.query(models.ChatRoom).count()
        active_rooms = db.query(models.ChatRoom).filter(models.ChatRoom.is_active == True).count()
        total_messages = db.query(models.ChatMessage).count()
        
        # Mensajes de hoy
        today = datetime.now().date()
        messages_today = db.query(models.ChatMessage).filter(
            models.ChatMessage.created_at >= today
        ).count()
        
        # Usuarios activos
        active_users = db.query(models.Users).filter(models.Users.is_active == True).count()
        
        return {
            "total_rooms": total_rooms,
            "active_rooms": active_rooms,
            "total_messages": total_messages,
            "messages_today": messages_today,
            "active_users": active_users
        }
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {e}")
        return {
            "total_rooms": 0,
            "active_rooms": 0,
            "total_messages": 0,
            "messages_today": 0,
            "active_users": 0
        }
