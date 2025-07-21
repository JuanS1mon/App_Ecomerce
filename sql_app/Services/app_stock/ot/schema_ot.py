from typing import Optional, List, Union

# Imports de bibliotecas estándar
from datetime import datetime

# Imports de terceros
from pydantic import BaseModel, ConfigDict

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
    estado: Optional[str] = "planificando"  # planificando, ejecutando, finalizada

class OperacionCreate(OperacionBase):
    pass

class OperacionUpdate(BaseModel):
    id: Optional[int] = None  # Para permitir actualización de operaciones existentes
    descripcion: Optional[str] = None
    responsable: Optional[str] = None
    tiempo_estimado: Optional[float] = None
    orden: Optional[int] = None
    estado: Optional[str] = None

class Operacion(OperacionBase):
    id: int
    reportes_tiempo: List[ReporteTiempo] = []  # Cambiado de "ReporteTiempo" a ReporteTiempo
    
    model_config = ConfigDict(from_attributes=True)

# Esquemas para OTMaterial (sin referencias circulares)
class OTMaterialBase(BaseModel):
    ot_id: int
    codigo_art: int
    id_deposito: int
    cantidad_planificada: float = 0.0
    observacion: Optional[str] = None

class OTMaterialCreate(OTMaterialBase):
    pass

class OTMaterialUpdate(BaseModel):
    cantidad_planificada: Optional[float] = None
    cantidad_utilizada: Optional[float] = None
    cantidad_devuelta: Optional[float] = None
    estado: Optional[str] = None
    observacion: Optional[str] = None
    usuario_consumo: Optional[str] = None

class OTMaterialConsumo(BaseModel):
    """Schema específico para registrar consumo de materiales"""
    cantidad_utilizada: float
    usuario_consumo: str
    observacion: Optional[str] = None

class OTMaterial(OTMaterialBase):
    id: int
    cantidad_utilizada: float
    cantidad_devuelta: float
    estado: str
    fecha_planificacion: datetime
    fecha_consumo: Optional[datetime] = None
    fecha_devolucion: Optional[datetime] = None
    usuario_consumo: Optional[str] = None
    nro_movimiento_stock: Optional[int] = None
    cantidad_pendiente: float
    porcentaje_utilizado: float
    
    model_config = ConfigDict(from_attributes=True)

# Esquemas para OT
class OTBase(BaseModel):
    numero: Optional[str] = None
    fecha: Optional[datetime] = None
    cliente: Optional[str] = None
    tipo: Optional[str] = None
    tecnico: Optional[str] = None
    descripcion: Optional[str] = None
    id_deposito: Optional[int] = None
    # Campos heredados del modelo anterior (para compatibilidad)
    id_trabajo: Optional[str] = None
    titulo: Optional[str] = None
    area: Optional[str] = None
    personal: Optional[str] = None
    tiempo_estimado: Optional[str] = None

class OTCreate(OTBase):
    estado: str = "planificando"  # Valor por defecto para el estado
    tareas: Optional[List[OperacionCreate]] = None  # Usar OperacionCreate directamente

class OTUpdate(BaseModel):
    numero: Optional[str] = None
    fecha: Optional[datetime] = None
    cliente: Optional[str] = None
    tipo: Optional[str] = None
    tecnico: Optional[str] = None
    descripcion: Optional[str] = None
    id_deposito: Optional[int] = None
    estado: Optional[str] = None
    tareas: Optional[List[OperacionUpdate]] = None  # Usar OperacionUpdate directamente

class OT(OTBase):
    id: int
    estado: str
    fecha_creacion: datetime
    fecha_inicio: Optional[datetime] = None
    fecha_fin: Optional[datetime] = None
    operaciones: List[Operacion] = []  # Cambiado de "Operacion" a Operacion
    materiales: List[OTMaterial] = []  # Cambiado de "OTMaterial" a OTMaterial
    
    # Campo calculado para el progreso
    progreso: Optional[float] = None
    
    model_config = ConfigDict(from_attributes=True)

# Agregar reconstrucción de modelos para resolver referencias adelantadas
Operacion.model_rebuild()
OTMaterial.model_rebuild()
OT.model_rebuild()