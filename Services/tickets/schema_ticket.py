# Imports de bibliotecas estándar
from datetime import datetime
from typing import Optional, List, Dict, Any

# Imports de terceros
from pydantic import BaseModel, ConfigDict

class HistorialItem(BaseModel):
    """Elemento individual del historial de un ticket"""
    fecha: datetime
    usuario: str
    rol: Optional[str] = None
    comentario: str

class TicketBase(BaseModel):
    """Clase base para el modelo de ticket"""
    titulo: str
    descripcion: str
    categoria: str
    prioridad: str  # baja, media, alta, critica
    
    # Campos opcionales
    solicitante: Optional[str] = None
    email: Optional[str] = None
    telefono: Optional[str] = None
    departamento: Optional[str] = None
    asignado_a: Optional[str] = None
    tiempo_estimado: Optional[int] = None  # en minutos
    tiempo_real: Optional[int] = None      # en minutos

class TicketCreate(TicketBase):
    """Esquema para crear un nuevo ticket"""
    estado: str = "abierto"  # valor por defecto
    
    # Para la creación no se permiten estos campos (se generan automáticamente)
    # fecha_creacion, ultima_actualizacion, historial

class TicketUpdate(BaseModel):
    """Esquema para actualizar un ticket existente"""
    titulo: Optional[str] = None
    descripcion: Optional[str] = None
    categoria: Optional[str] = None
    prioridad: Optional[str] = None
    estado: Optional[str] = None
    solicitante: Optional[str] = None
    email: Optional[str] = None
    telefono: Optional[str] = None
    departamento: Optional[str] = None
    asignado_a: Optional[str] = None
    tiempo_estimado: Optional[int] = None
    tiempo_real: Optional[int] = None
    
    # Campos adicionales para gestionar el historial
    comentario: Optional[str] = None
    usuario_modificacion: Optional[str] = None

class TicketRead(TicketBase):
    """Esquema para leer un ticket"""
    id: int
    estado: str
    fecha_creacion: datetime
    ultima_actualizacion: Optional[datetime] = None
    historial: Optional[List[Dict[str, Any]]] = None
    
    model_config = ConfigDict(from_attributes=True)

class TicketStats(BaseModel):
    """Esquema para estadísticas de tickets"""
    total: int
    abiertos: int
    proceso: int
    cerrados: int
    comparacion: Dict[str, int]
    porEstado: List[int]
    porCategoria: List[int]
    tendencia: Dict[str, List[int]]
    porPrioridad: List[int]
    ticketsRecientes: Optional[List[Dict[str, Any]]] = None
    ticketsCriticos: Optional[List[Dict[str, Any]]] = None
    
    model_config = ConfigDict(from_attributes=True)