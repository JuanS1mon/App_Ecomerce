# Imports de terceros
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

# Imports del proyecto
from ....db.database import Base

class MovementType(str, enum.Enum):
    PRESTAMO = "prestamo"
    VENTA = "venta" 
    CESION = "cesion"
    TRASLADO = "traslado"
    EXHIBICION = "exhibicion"

class MovementStatus(str, enum.Enum):
    ACTIVO = "activo"
    FINALIZADO = "finalizado"
    CANCELADO = "cancelado"

class Movements(Base):
    __tablename__ = 'movements'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    artwork_id = Column(Integer, ForeignKey('artworks.id'), nullable=False)
    movement_type = Column(SQLEnum(MovementType), nullable=False)
    status = Column(SQLEnum(MovementStatus), default=MovementStatus.ACTIVO)
    
    # Fechas
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Ubicaciones
    from_location_id = Column(Integer, ForeignKey('locations.id'), nullable=True)
    to_location_id = Column(Integer, ForeignKey('locations.id'), nullable=True)
    
    # Información de contacto
    contact_name = Column(String(255), nullable=True)
    contact_email = Column(String(255), nullable=True)
    contact_phone = Column(String(50), nullable=True)
    
    # Notas y referencias
    notes = Column(Text, nullable=True)
    reference_document = Column(String(255), nullable=True)
    
    # Referencias a otros módulos
    sale_id = Column(Integer, ForeignKey('sales.id'), nullable=True)
    exhibition_id = Column(Integer, ForeignKey('exhibitions.id'), nullable=True)
    
    # Relaciones
    artwork = relationship("Artworks", back_populates="movements")
    from_location = relationship("Locations", foreign_keys=[from_location_id], back_populates="movements_from")
    to_location = relationship("Locations", foreign_keys=[to_location_id], back_populates="movements_to")
    sale = relationship("Sales", back_populates="movement")
    exhibition = relationship("Exhibitions", back_populates="movements")
