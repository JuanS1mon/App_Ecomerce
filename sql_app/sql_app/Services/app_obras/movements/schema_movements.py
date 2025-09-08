# Imports de terceros
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

# Enums para validación
class MovementTypeEnum(str, Enum):
    PRESTAMO = "prestamo"
    VENTA = "venta"
    CESION = "cesion"
    TRASLADO = "traslado"
    EXHIBICION = "exhibicion"

class MovementStatusEnum(str, Enum):
    ACTIVO = "activo"
    FINALIZADO = "finalizado"
    CANCELADO = "cancelado"

# Schemas para Contacts
class ContactBase(BaseModel):
    name: str = Field(..., description="Nombre del contacto")
    email: Optional[str] = Field(None, description="Email del contacto")
    phone: Optional[str] = Field(None, description="Teléfono del contacto")
    organization: Optional[str] = Field(None, description="Organización")
    position: Optional[str] = Field(None, description="Cargo/Posición")
    address: Optional[str] = Field(None, description="Dirección")
    notes: Optional[str] = Field(None, description="Notas adicionales")

class ContactCreate(ContactBase):
    pass

class ContactUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    organization: Optional[str] = None
    position: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None

class ContactResponse(ContactBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Schemas para Movements
class MovementBase(BaseModel):
    artwork_id: int = Field(..., description="ID de la obra de arte")
    movement_type: MovementTypeEnum = Field(..., description="Tipo de movimiento")
    status: MovementStatusEnum = Field(MovementStatusEnum.ACTIVO, description="Estado del movimiento")
    
    start_date: Optional[datetime] = Field(None, description="Fecha de inicio del movimiento")
    end_date: Optional[datetime] = Field(None, description="Fecha de finalización del movimiento")
    
    from_location_id: Optional[int] = Field(None, description="Ubicación de origen")
    to_location_id: Optional[int] = Field(None, description="Ubicación de destino")
    
    contact_name: Optional[str] = Field(None, description="Nombre del contacto")
    contact_email: Optional[str] = Field(None, description="Email del contacto")
    contact_phone: Optional[str] = Field(None, description="Teléfono del contacto")
    
    notes: Optional[str] = Field(None, description="Notas del movimiento")
    reference_document: Optional[str] = Field(None, description="Documento de referencia")
    
    sale_id: Optional[int] = Field(None, description="ID de venta relacionada")
    exhibition_id: Optional[int] = Field(None, description="ID de exhibición relacionada")

class MovementCreate(MovementBase):
    pass

class MovementUpdate(BaseModel):
    movement_type: Optional[MovementTypeEnum] = None
    status: Optional[MovementStatusEnum] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    from_location_id: Optional[int] = None
    to_location_id: Optional[int] = None
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    notes: Optional[str] = None
    reference_document: Optional[str] = None
    sale_id: Optional[int] = None
    exhibition_id: Optional[int] = None

class MovementResponse(MovementBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Schema para movimientos agrupados
class GroupedMovementCreate(BaseModel):
    artwork_ids: List[int] = Field(..., description="Lista de IDs de obras")
    movement_type: MovementTypeEnum = Field(..., description="Tipo de movimiento")
    status: MovementStatusEnum = Field(MovementStatusEnum.ACTIVO, description="Estado del movimiento")
    
    start_date: Optional[datetime] = Field(None, description="Fecha de inicio del movimiento")
    end_date: Optional[datetime] = Field(None, description="Fecha de finalización del movimiento")
    
    from_location_id: Optional[int] = Field(None, description="Ubicación de origen")
    to_location_id: Optional[int] = Field(None, description="Ubicación de destino")
    
    contact_name: Optional[str] = Field(None, description="Nombre del contacto")
    contact_email: Optional[str] = Field(None, description="Email del contacto")
    contact_phone: Optional[str] = Field(None, description="Teléfono del contacto")
    
    notes: Optional[str] = Field(None, description="Notas del movimiento")
    reference_document: Optional[str] = Field(None, description="Documento de referencia")

class MovementHistoryResponse(BaseModel):
    artwork_id: int
    movements: List[MovementResponse]
    current_location: Optional[str] = None

    class Config:
        from_attributes = True
