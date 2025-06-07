from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# Esquemas para Operaciones
class OperacionBase(BaseModel):
    descripcion: str
    tiempo_estimado: float = 0.0
    estado: str = "pendiente"
    costo: float = 0.0

class OperacionCreate(OperacionBase):
    pass

class OperacionUpdate(BaseModel):
    descripcion: Optional[str] = None
    tiempo_estimado: Optional[float] = None
    estado: Optional[str] = None
    costo: Optional[float] = None

class Operacion(OperacionBase):
    id: int
    orden_trabajo_id: int
    
    class Config:
        orm_mode = True

# Esquemas para Reportes de Tiempo
class ReporteTiempoBase(BaseModel):
    tecnico_id: int
    fecha_inicio: datetime = Field(default_factory=datetime.now)
    fecha_fin: Optional[datetime] = None
    descripcion: Optional[str] = None
    duracion: float = 0.0

class ReporteTiempoCreate(ReporteTiempoBase):
    pass

class ReporteTiempoUpdate(BaseModel):
    fecha_fin: Optional[datetime] = None
    descripcion: Optional[str] = None
    duracion: Optional[float] = None

class ReporteTiempo(ReporteTiempoBase):
    id: int
    orden_trabajo_id: int
    
    class Config:
        orm_mode = True

# Esquemas para Órdenes de Trabajo
class OrdenTrabajoBase(BaseModel):
    numero: str
    cliente_id: int
    descripcion: str
    fecha_entrega: Optional[datetime] = None
    estado: str = "pendiente"
    prioridad: str = "normal"
    tecnico_id: Optional[int] = None
    notas: Optional[str] = None
    costo_total: float = 0.0

class OrdenTrabajoCreate(OrdenTrabajoBase):
    operaciones: Optional[List[OperacionCreate]] = []

class OrdenTrabajoUpdate(BaseModel):
    descripcion: Optional[str] = None
    fecha_entrega: Optional[datetime] = None
    estado: Optional[str] = None
    prioridad: Optional[str] = None
    tecnico_id: Optional[int] = None
    notas: Optional[str] = None
    costo_total: Optional[float] = None

class OrdenTrabajo(OrdenTrabajoBase):
    id: int
    fecha_creacion: datetime
    operaciones: List[Operacion] = []
    reportes_tiempo: List[ReporteTiempo] = []
    
    class Config:
        orm_mode = True