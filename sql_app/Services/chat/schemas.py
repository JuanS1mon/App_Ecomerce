"""
Esquemas Pydantic para el sistema de chat
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class TipoSala(str, Enum):
    PUBLICO = "publico"
    PRIVADO = "privado"
    GRUPO = "grupo"

class TipoMensaje(str, Enum):
    TEXTO = "texto"
    IMAGEN = "imagen"
    ARCHIVO = "archivo"
    SISTEMA = "sistema"

class RolMiembro(str, Enum):
    ADMIN = "admin"
    MODERADOR = "moderador"
    MIEMBRO = "miembro"

# Esquemas para Salas de Chat
class ChatRoomBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100)
    descripcion: Optional[str] = None
    tipo: TipoSala = TipoSala.PUBLICO

class ChatRoomCreate(ChatRoomBase):
    pass

class ChatRoomResponse(ChatRoomBase):
    id: int
    activo: bool
    creado_por: int
    fecha_creacion: datetime
    total_miembros: int = 0
    ultimo_mensaje: Optional[str] = None
    mensajes_no_leidos: int = 0
    
    class Config:
        from_attributes = True

# Esquemas para Mensajes
class ChatMessageBase(BaseModel):
    contenido: str = Field(..., min_length=1)
    tipo: TipoMensaje = TipoMensaje.TEXTO

class ChatMessageCreate(ChatMessageBase):
    sala_id: int
    usuario_id: int

class ChatMessageUpdate(BaseModel):
    contenido: Optional[str] = None

class ChatMessageResponse(ChatMessageBase):
    id: int
    sala_id: int
    usuario_id: int
    fecha_envio: datetime
    editado: bool
    fecha_edicion: Optional[datetime]
    eliminado: bool
    
    # Información del usuario
    nombre_usuario: Optional[str] = None
    avatar_usuario: Optional[str] = None
    
    class Config:
        from_attributes = True

# Esquemas para Miembros
class ChatMemberBase(BaseModel):
    rol: RolMiembro = RolMiembro.MIEMBRO

class ChatMemberCreate(ChatMemberBase):
    sala_id: int
    usuario_id: int

class ChatMemberResponse(ChatMemberBase):
    id: int
    sala_id: int
    usuario_id: int
    fecha_union: datetime
    activo: bool
    
    # Información del usuario
    nombre_usuario: Optional[str] = None
    email_usuario: Optional[str] = None
    
    class Config:
        from_attributes = True

# Esquemas para WebSocket
class ChatWebSocketMessage(BaseModel):
    type: str
    data: Optional[dict] = None
    timestamp: Optional[str] = None
    sala_id: Optional[int] = None
    usuario_id: Optional[int] = None

class ChatNotificacion(BaseModel):
    tipo: str
    sala_id: int
    mensaje: Optional[ChatMessageResponse] = None
    usuario: Optional[str] = None
    timestamp: str

# Esquemas para estadísticas
class ChatEstadisticas(BaseModel):
    total_salas: int
    total_mensajes: int
    salas_activas: int
    usuarios_conectados: int
    mensajes_hoy: int

class SalaConMensajes(BaseModel):
    sala: ChatRoomResponse
    mensajes: List[ChatMessageResponse]
    miembros: List[ChatMemberResponse]
