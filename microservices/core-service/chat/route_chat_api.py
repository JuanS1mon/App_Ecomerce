"""
Router básico para API de chat de prueba
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Dict, Any
from pydantic import BaseModel
from datetime import datetime

from db.database import get_db

router = APIRouter(prefix="/api/chat", tags=["chat"])

# Schemas básicos
class ChatMessageCreate(BaseModel):
    room_id: int
    user_id: str
    user_name: str
    message: str

class ChatMessageResponse(BaseModel):
    id: int
    room_id: int
    user_id: str
    user_name: str
    message: str
    created_at: datetime

class ChatRoomResponse(BaseModel):
    id: int
    name: str
    description: str

@router.get("/salas", response_model=List[ChatRoomResponse])
async def obtener_salas(db: Session = Depends(get_db)):
    """Obtener todas las salas de chat"""
    try:
        result = db.execute(text("""
            SELECT id, name, description
            FROM chat_rooms
            ORDER BY id
        """)).fetchall()
        
        salas = []
        for row in result:
            salas.append({
                "id": row[0],
                "name": row[1],
                "description": row[2] or ""
            })
        
        return salas
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo salas: {str(e)}")

@router.get("/rooms/{room_id}/messages", response_model=List[ChatMessageResponse])
async def obtener_mensajes_sala(room_id: int, db: Session = Depends(get_db)):
    """Obtener mensajes de una sala específica"""
    try:
        result = db.execute(text("""
            SELECT id, room_id, user_id, user_name, message, created_at
            FROM chat_messages
            WHERE room_id = :room_id
            ORDER BY created_at ASC
        """), {"room_id": room_id}).fetchall()
        
        mensajes = []
        for row in result:
            mensajes.append({
                "id": row[0],
                "room_id": row[1],
                "user_id": row[2],
                "user_name": row[3],
                "message": row[4],
                "created_at": row[5]
            })
        
        return mensajes
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo mensajes: {str(e)}")

@router.post("/messages")
async def crear_mensaje_chat(mensaje: ChatMessageCreate, db: Session = Depends(get_db)):
    """Crear un nuevo mensaje de chat"""
    try:
        # Verificar que la sala existe
        sala_exists = db.execute(text("""
            SELECT id FROM chat_rooms WHERE id = :room_id
        """), {"room_id": mensaje.room_id}).fetchone()
        
        if not sala_exists:
            raise HTTPException(status_code=404, detail="Sala no encontrada")
        
        # Insertar el mensaje
        result = db.execute(text("""
            INSERT INTO chat_messages (room_id, user_id, user_name, message)
            OUTPUT INSERTED.id
            VALUES (:room_id, :user_id, :user_name, :message)
        """), {
            "room_id": mensaje.room_id,
            "user_id": mensaje.user_id,
            "user_name": mensaje.user_name,
            "message": mensaje.message
        })
        
        mensaje_id = result.scalar()
        db.commit()
        
        return {
            "id": mensaje_id,
            "room_id": mensaje.room_id,
            "user_id": mensaje.user_id,
            "user_name": mensaje.user_name,
            "message": mensaje.message,
            "created_at": datetime.now(),
            "status": "created"
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creando mensaje: {str(e)}")

@router.get("/rooms/{room_id}/info")
async def obtener_info_sala(room_id: int, db: Session = Depends(get_db)):
    """Obtener información detallada de una sala"""
    try:
        result = db.execute(text("""
            SELECT 
                r.id,
                r.name,
                r.description,
                COUNT(m.id) as total_mensajes
            FROM chat_rooms r
            LEFT JOIN chat_messages m ON r.id = m.room_id
            WHERE r.id = :room_id
            GROUP BY r.id, r.name, r.description
        """), {"room_id": room_id}).fetchone()
        
        if not result:
            raise HTTPException(status_code=404, detail="Sala no encontrada")
        
        return {
            "id": result[0],
            "name": result[1],
            "description": result[2] or "",
            "total_mensajes": result[3] or 0
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo info de sala: {str(e)}")

@router.get("/estadisticas")
async def obtener_estadisticas_chat(db: Session = Depends(get_db)):
    """Obtener estadísticas generales del chat"""
    try:
        # Total de salas
        total_salas = db.execute(text("SELECT COUNT(*) FROM chat_rooms")).scalar()
        
        # Total de mensajes
        total_mensajes = db.execute(text("SELECT COUNT(*) FROM chat_messages")).scalar()
        
        # Mensajes de hoy
        mensajes_hoy = db.execute(text("""
            SELECT COUNT(*) 
            FROM chat_messages 
            WHERE CAST(created_at AS DATE) = CAST(GETDATE() AS DATE)
        """)).scalar()
        
        return {
            "total_salas": total_salas or 0,
            "total_mensajes": total_mensajes or 0,
            "mensajes_hoy": mensajes_hoy or 0,
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo estadísticas: {str(e)}")
