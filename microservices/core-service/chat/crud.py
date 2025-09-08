"""
CRUD operations para Chat
"""

from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from datetime import datetime

from .models import ChatMessage, ChatRoom, ChatMember
from .schemas import ChatMessageCreate, ChatMessageUpdate


class ChatCrud:
    """CRUD para operaciones de chat"""
    
    @staticmethod
    def create_message(db: Session, message: ChatMessageCreate) -> ChatMessage:
        """Crear un nuevo mensaje"""
        db_message = ChatMessage(
            sala_id=message.sala_id,
            usuario_id=message.usuario_id,
            contenido=message.contenido,
            tipo=message.tipo
        )
        db.add(db_message)
        db.commit()
        db.refresh(db_message)
        return db_message
    
    @staticmethod
    def get_messages_by_room(db: Session, room_id: int, limit: int = 50, offset: int = 0) -> List[ChatMessage]:
        """Obtener mensajes de una sala"""
        return db.query(ChatMessage)\
                 .filter(ChatMessage.sala_id == room_id)\
                 .filter(ChatMessage.eliminado == False)\
                 .order_by(desc(ChatMessage.fecha_envio))\
                 .limit(limit)\
                 .offset(offset)\
                 .all()
    
    @staticmethod
    def get_recent_messages_by_room(db: Session, room_id: int, limit: int = 20) -> List[ChatMessage]:
        """Obtener mensajes recientes de una sala"""
        return db.query(ChatMessage)\
                 .filter(ChatMessage.sala_id == room_id)\
                 .filter(ChatMessage.eliminado == False)\
                 .order_by(ChatMessage.fecha_envio)\
                 .limit(limit)\
                 .all()
    
    @staticmethod
    def get_unread_messages_for_user(db: Session, user_id: int, room_id: int) -> List[ChatMessage]:
        """Obtener mensajes no leídos para un usuario en una sala"""
        # Por simplicidad, retornamos los últimos 10 mensajes
        # En una implementación completa, se usaría ChatReadStatus
        return db.query(ChatMessage)\
                 .filter(ChatMessage.sala_id == room_id)\
                 .filter(ChatMessage.usuario_id != user_id)\
                 .filter(ChatMessage.eliminado == False)\
                 .order_by(desc(ChatMessage.fecha_envio))\
                 .limit(10)\
                 .all()
    
    @staticmethod
    def get_or_create_room(db: Session, room_id: int = 1, name: str = "Sala General") -> ChatRoom:
        """Obtener o crear una sala de chat"""
        room = db.query(ChatRoom).filter(ChatRoom.id == room_id).first()
        if not room:
            room = ChatRoom(
                id=room_id,
                nombre=name,
                descripcion="Sala de chat general",
                tipo="publico",
                creado_por=1  # Admin por defecto
            )
            db.add(room)
            db.commit()
            db.refresh(room)
        return room
    
    @staticmethod
    def send_message_to_admin(db: Session, user_id: int, user_name: str, message: str) -> ChatMessage:
        """Enviar mensaje al admin (sala especial)"""
        # Crear o obtener sala de soporte (ID = 999)
        support_room = ChatCrud.get_or_create_room(
            db, 
            room_id=999, 
            name=f"Soporte - {user_name}"
        )
        
        # Crear el mensaje
        message_data = ChatMessageCreate(
            sala_id=support_room.id,
            usuario_id=user_id,
            contenido=message,
            tipo="texto"
        )
        
        return ChatCrud.create_message(db, message_data)


# Instancia global
chat_crud = ChatCrud()
