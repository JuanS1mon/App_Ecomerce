"""
Router para API REST del Chat
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

from ...db.database import get_db
from .crud import chat_crud
from .schemas import ChatMessageCreate, ChatMessageResponse
from .models import ChatMessage

router = APIRouter(
    prefix="/api/chat",
    tags=["chat"]
)

class SendMessageRequest(BaseModel):
    """Request para enviar mensaje al admin"""
    message: str
    user_name: str = "Usuario Anónimo"
    user_id: int = 9999  # ID por defecto para usuarios no autenticados

class SendMessageResponse(BaseModel):
    """Response del mensaje enviado"""
    success: bool
    message_id: int
    message: str
    timestamp: str

@router.post("/send-to-admin", response_model=SendMessageResponse)
async def send_message_to_admin(
    request: SendMessageRequest,
    db: Session = Depends(get_db)
):
    """
    Enviar mensaje al admin cuando el chat está desconectado
    """
    try:
        from datetime import datetime
        from sqlalchemy.sql import text
        
        # Insertar mensaje directamente con SQL
        current_time = datetime.utcnow()
        
        sql = text("""
            INSERT INTO chat_messages (room_id, user_id, user_name, message, created_at)
            VALUES (:room_id, :user_id, :user_name, :message, :created_at)
        """)
        
        result = db.execute(sql, {
            'room_id': 1,  # Sala general
            'user_id': str(request.user_id),
            'user_name': request.user_name,
            'message': request.message,
            'created_at': current_time
        })
        
        db.commit()
        
        # Obtener el ID del mensaje insertado
        message_id = result.lastrowid
        
        return SendMessageResponse(
            success=True,
            message_id=int(message_id) if message_id else 0,
            message=f"Mensaje enviado al admin: '{request.message}'",
            timestamp=current_time.isoformat()
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error enviando mensaje: {str(e)}"
        )

@router.get("/admin/messages")
async def get_admin_messages(
    db: Session = Depends(get_db),
    limit: int = 20
):
    """
    Obtener mensajes enviados al admin
    """
    try:
        from sqlalchemy.sql import text
        
        sql = text("""
            SELECT TOP(:limit) id, sala_id, usuario_id, contenido, tipo, fecha_envio, editado, eliminado
            FROM chat_messages 
            WHERE sala_id = 999 
            ORDER BY fecha_envio DESC
        """)
        
        result = db.execute(sql, {'limit': limit})
        messages = []
        
        for row in result:
            messages.append({
                "id": row.id,
                "sala_id": row.sala_id,
                "usuario_id": row.usuario_id,
                "contenido": row.contenido,
                "tipo": row.tipo,
                "fecha_envio": row.fecha_envio.isoformat() if row.fecha_envio else None,
                "editado": row.editado,
                "eliminado": row.eliminado
            })
        
        return {
            "success": True,
            "messages": messages,
            "total": len(messages)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo mensajes: {str(e)}"
        )

@router.get("/admin/messages", response_model=List[dict])
async def get_admin_messages(
    db: Session = Depends(get_db),
    limit: int = 50
):
    """
    Obtener mensajes enviados al admin (sala de soporte)
    """
    try:
        # Obtener mensajes de la sala de soporte (ID = 999)
        messages = chat_crud.get_messages_by_room(db, room_id=999, limit=limit)
        
        # Formatear respuesta
        formatted_messages = []
        for msg in messages:
            formatted_messages.append({
                "id": msg.id,
                "user_id": msg.usuario_id,
                "content": msg.contenido,
                "timestamp": msg.fecha_envio.isoformat(),
                "type": msg.tipo
            })
        
        return formatted_messages
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo mensajes: {str(e)}"
        )

@router.get("/room/{room_id}/messages")
async def get_room_messages(
    room_id: int = 1,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    Obtener mensajes de una sala de chat
    """
    try:
        from sqlalchemy.sql import text
        
        sql = text("""
            SELECT TOP (:limit) id, user_id, user_name, message, created_at 
            FROM chat_messages 
            WHERE room_id = :room_id 
            ORDER BY created_at DESC
        """)
        
        result = db.execute(sql, {
            'room_id': room_id,
            'limit': limit
        })
        
        messages = []
        for row in result:
            messages.append({
                "id": row[0],
                "user_id": row[1],
                "user_name": row[2],
                "message": row[3],
                "timestamp": row[4].isoformat() if row[4] else None,
                "room_id": room_id
            })
        
        # Revertir para mostrar en orden cronológico
        messages.reverse()
        
        return {
            "success": True,
            "messages": messages,
            "count": len(messages)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo mensajes: {str(e)}"
        )
