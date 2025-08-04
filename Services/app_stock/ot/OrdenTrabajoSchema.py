# Imports de bibliotecas estándar
from datetime import datetime
from typing import List, Optional

# Imports de terceros
from pydantic import BaseModel, Field

# Esquemas para Operación
class OperacionBase(BaseModel):
    descripcion: str
    tiempo_estimado: float = Field(default=0.0, ge=0.0)
    estado: str = "Pendiente"
    costo: float = Field(default=0.0, ge=0.0)

class OperacionCreate(OperacionBase):
    pass

class Operacion(OperacionBase):
    id: int
    orden_trabajo_id: int

    class Config:
        orm_mode = True

# Esquemas para Reporte de Tiempo
class ReporteTiempoBase(BaseModel):
    tecnico_id: int
    fecha_inicio: datetime = Field(default_factory=datetime.now)
    fecha_fin: Optional[datetime] = None
    descripcion: Optional[str] = None
    duracion: float = Field(default=0.0, ge=0.0)

class ReporteTiempoCreate(ReporteTiempoBase):
    orden_trabajo_id: int

class ReporteTiempo(ReporteTiempoBase):
    id: int
    orden_trabajo_id: int

    class Config:
        orm_mode = True

# Esquemas para Orden de Trabajo
class OrdenTrabajoBase(BaseModel):
    numero: str
    cliente_id: int
    descripcion: str
    fecha_entrega: Optional[datetime] = None
    estado: str = "Pendiente"
    prioridad: str = "Normal"
    tecnico_id: Optional[int] = None
    notas: Optional[str] = None

class OrdenTrabajoCreate(OrdenTrabajoBase):
    operaciones: Optional[List[OperacionCreate]] = []

class OrdenTrabajoUpdate(BaseModel):
    numero: Optional[str] = None
    cliente_id: Optional[int] = None
    descripcion: Optional[str] = None
    fecha_entrega: Optional[datetime] = None
    estado: Optional[str] = None
    prioridad: Optional[str] = None
    tecnico_id: Optional[int] = None
    notas: Optional[str] = None
    fecha_cierre: Optional[datetime] = None

class OrdenTrabajo(OrdenTrabajoBase):
    id: int
    fecha_creacion: datetime
    fecha_cierre: Optional[datetime] = None
    costo_total: float
    operaciones: List[Operacion] = []
    reportes_tiempo: List[ReporteTiempo] = []

    class Config:
        orm_mode = True