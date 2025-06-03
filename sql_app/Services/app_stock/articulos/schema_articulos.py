from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict
from datetime import date, datetime

class ArticulosBase(BaseModel):
    codigo: str
    descripcion: str
    preciocosto: float
    precioventa: float
    modelo: str
    marca: str
    id_tipo: str
    codigo_barras: Optional[str] = None
    codigo_barras_tipo: Optional[str] = None
    qr_data: Optional[str] = None
    imagen_codigo_url: Optional[str] = None

class ArticulosCreate(ArticulosBase):
    id: Optional[int] = None

class ArticulosUpdate(BaseModel):
    codigo: Optional[str] = None
    descripcion: Optional[str] = None
    preciocosto: Optional[float] = None
    precioventa: Optional[float] = None
    modelo: Optional[str] = None
    marca: Optional[str] = None
    id_tipo: Optional[str] = None
    codigo_barras: Optional[str] = None
    codigo_barras_tipo: Optional[str] = None
    qr_data: Optional[str] = None
    imagen_codigo_url: Optional[str] = None

class ArticulosRead(ArticulosBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class CodigoBarrasRequest(BaseModel):
    tipo: str  # 'ean13', 'code128', 'ean8', 'upca'
    valor: Optional[str] = None  # Si se deja vacío, se generará automáticamente
    guardar_en_db: bool = True

class QRCodeRequest(BaseModel):
    datos: str  # Datos a almacenar en el QR (pueden ser JSON u otros datos)
    version: Optional[int] = None  # Versión del QR (1-40) - determina la capacidad y tamaño
    box_size: int = 10  # Tamaño de cada caja del QR
    border: int = 4  # Borde del QR
    guardar_en_db: bool = True