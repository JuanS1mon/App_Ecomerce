from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

# Esquemas para ReporteTiempo
class ReporteTiempoBase(BaseModel):
    operacion_id: int
    horas: float
    usuario: str
    descripcion: Optional[str] = None

class ReporteTiempoCreate(ReporteTiempoBase):
    continuar_iteracion: Optional[bool] = True  # True por defecto - el usuario desea continuar

class ReporteTiempoUpdate(BaseModel):
    horas: Optional[float] = None
    usuario: Optional[str] = None
    descripcion: Optional[str] = None

class ReporteTiempo(ReporteTiempoBase):
    id: int
    fecha: datetime
    
    model_config = ConfigDict(from_attributes=True)

# Esquemas para Operacion
class OperacionBase(BaseModel):
    ot_id: int
    descripcion: str
    responsable: Optional[str] = None
    tiempo_estimado: Optional[float] = None
    orden: Optional[int] = 1
    estado: Optional[str] = "pendiente"

class OperacionCreate(OperacionBase):
    pass

class OperacionUpdate(BaseModel):
    descripcion: Optional[str] = None
    responsable: Optional[str] = None
    tiempo_estimado: Optional[float] = None
    orden: Optional[int] = None
    estado: Optional[str] = None

class Operacion(OperacionBase):
    id: int
    reportes_tiempo: List[ReporteTiempo] = []
    
    model_config = ConfigDict(from_attributes=True)

# Esquemas para OT
class OTBase(BaseModel):
    id_trabajo: str
    titulo: Optional[str] = None
    area: Optional[str] = None
    personal: Optional[str] = None
    tiempo_estimado: Optional[str] = None
    descripcion: Optional[str] = None
    id_deposito: Optional[int] = None

class OTCreate(OTBase):
    estado: str = "pendiente"  # Valor por defecto para el estado

class OTUpdate(BaseModel):
    id_trabajo: Optional[str] = None
    titulo: Optional[str] = None
    area: Optional[str] = None
    personal: Optional[str] = None
    tiempo_estimado: Optional[str] = None
    descripcion: Optional[str] = None
    id_deposito: Optional[int] = None
    estado: Optional[str] = None

class OT(OTBase):
    id: int
    estado: str
    fecha_creacion: datetime
    fecha_inicio: Optional[datetime] = None
    fecha_fin: Optional[datetime] = None
    operaciones: List[Operacion] = []
    
    model_config = ConfigDict(from_attributes=True)