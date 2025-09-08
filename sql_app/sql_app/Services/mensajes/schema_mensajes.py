from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum

class TipoMensaje(str, Enum):
    USUARIO = "usuario"
    SISTEMA = "sistema"
    ALERTA = "alerta"
    NOTIFICACION = "notificacion"

class PrioridadMensaje(str, Enum):
    BAJA = "baja"
    NORMAL = "normal"
    ALTA = "alta"
    URGENTE = "urgente"

class MensajeBase(BaseModel):
    titulo: str = Field(..., min_length=1, max_length=200)
    contenido: str = Field(..., min_length=1)
    tipo: TipoMensaje = TipoMensaje.USUARIO
    prioridad: PrioridadMensaje = PrioridadMensaje.NORMAL
    metadatos: Optional[str] = None

class MensajeCreate(MensajeBase):
    usuario_receptor_id: int
    usuario_emisor_id: Optional[int] = None  # None para mensajes del sistema

class MensajeUpdate(BaseModel):
    titulo: Optional[str] = None
    contenido: Optional[str] = None
    tipo: Optional[TipoMensaje] = None
    prioridad: Optional[PrioridadMensaje] = None
    leido: Optional[bool] = None
    metadatos: Optional[str] = None

class MensajeResponse(MensajeBase):
    id: int
    usuario_emisor_id: Optional[int]
    usuario_receptor_id: int
    leido: bool
    fecha_creacion: datetime
    fecha_lectura: Optional[datetime]
    activo: bool
    
    # Información adicional del emisor y receptor
    nombre_emisor: Optional[str] = None
    nombre_receptor: Optional[str] = None

    class Config:
        from_attributes = True

class MensajeResumen(BaseModel):
    """Para mostrar en notificaciones de la navbar"""
    id: int
    titulo: str
    tipo: TipoMensaje
    prioridad: PrioridadMensaje
    leido: bool
    fecha_creacion: datetime
    nombre_emisor: Optional[str] = None

class EstadisticasMensajes(BaseModel):
    total_mensajes: int
    mensajes_no_leidos: int
    mensajes_por_tipo: dict
    mensajes_por_prioridad: dict

# Nuevos esquemas para notificaciones WebSocket

class TipoNotificacion(str, Enum):
    NEW_MESSAGE = "new_message"
    MESSAGE_UPDATED = "message_updated"
    MESSAGE_READ = "message_read"
    URGENT_MESSAGE = "urgent_message"
    SYSTEM_NOTIFICATION = "system_notification"
    CONNECTION_ESTABLISHED = "connection_established"
    CONNECTION_STATS = "connection_stats"
    PING = "ping"
    PONG = "pong"
    ERROR = "error"

class NotificacionMensaje(BaseModel):
    type: TipoNotificacion
    data: Optional[dict] = None
    message: Optional[str] = None
    timestamp: Optional[str] = None
    user_id: Optional[int] = None

class NotificacionNuevoMensaje(BaseModel):
    id: int
    title: str
    content: str
    tipo: TipoMensaje
    prioridad: PrioridadMensaje
    usuario_receptor_id: int
    timestamp: str

class EstadisticasConexion(BaseModel):
    total_users_connected: int
    total_user_connections: int
    total_admin_connections: int
    total_connections: int
    users_online: List[int]

class WebSocketMessage(BaseModel):
    type: str
    data: Optional[dict] = None
    timestamp: Optional[str] = None
