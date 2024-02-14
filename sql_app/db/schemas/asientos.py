from pydantic import BaseModel,validator
from typing import Optional
from datetime import datetime
from typing import List



class Asiento_respuesta(BaseModel):
    asiento: int
    respuesta: str

class AsientoDetalle(BaseModel):
    cuenta: str
    signo: str
    importe: float
    detalle: str
    centro_costo: str

    @validator('importe')
    def validate_importe(cls, value):
        if value < 0:
            raise ValueError('importe no puede ser negativo')
        return value

class AsientoDetalleRespuesta(BaseModel):
    NumeroRegistro: int
    descripcion: str
    signo: str
    importeD: float
    importeH: float
    Detalle: str
    CentroCosto: str

class AsientoRespuesta(BaseModel):
    asiento: int
    fecha: str
    detalle: str
    tipomovimiento: int
    asiento_detalle: List[AsientoDetalleRespuesta]

    @validator('fecha', pre=True)
    def format_fecha(cls, v):
        if isinstance(v, datetime):
            return v.strftime('%d-%m-%Y')
        return v


class Asiento(BaseModel):
    fecha: str
    detalle: str
    tipomovimiento: int
    asiento_detalle: List[AsientoDetalle]

    @validator('fecha')
    def parse_fecha(cls, v):
        return datetime.strptime(v, '%d-%m-%Y')
    
    @validator('tipomovimiento')
    def validate_tipomovimiento(cls, value):
        if value < 0:
            raise ValueError('tipomovimiento no puede ser negativo')
        return value

class AsientoDetalle_Create(BaseModel):
    cuenta: Optional[str] = None
    signo: Optional[str] = None
    importe: Optional[float] = None
    detalle: Optional[str] = None
    centro_costo: Optional[str] = None


class BusquedaAsientos(BaseModel):

    fechadesde: Optional[str] = None
    fechahasta: Optional[str] = None
    TipodeMovimiento: Optional[list[int]] = None
    codigos_asientos: Optional[List[int]] = None

    @validator('fechadesde', 'fechahasta', pre=True)
    def parse_date(cls, v):
        return datetime.strptime(v, "%d-%m-%Y") if v else None
    
class AsientoDetalleRespuestas(BaseModel):
    cuenta: int
    signo: str
    importe: float
    detalle: float
    centro_costo: str

class AsientoRespuestas(BaseModel):
    asiento: int
    fecha: str
    detalle: str
    tipomovimiento: int
    asiento_detalle: List[AsientoDetalleRespuestas]

    @validator('fecha', pre=True)
    def format_fecha(cls, v):
        if isinstance(v, datetime):
            return v.strftime('%d-%m-%Y')
        return v