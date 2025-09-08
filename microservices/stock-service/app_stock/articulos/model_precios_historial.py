# Imports de terceros
from sqlalchemy import Column, Integer, String, Boolean, Float, Date, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

# Imports del proyecto
from ....db.database import Base

class PreciosHistorial(Base):
    __tablename__ = 'precios_historial'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    articulo_id = Column(Integer, ForeignKey('articulos.id', ondelete='CASCADE'), nullable=False, index=True)
    precio_anterior = Column(Float, nullable=False)
    precio_nuevo = Column(Float, nullable=False)
    tipo_precio = Column(String(10), nullable=False)  # 'costo' o 'venta'
    fecha_cambio = Column(DateTime, default=func.current_timestamp(), nullable=False)
    usuario_id = Column(Integer, nullable=True)  # ID del usuario que realizó el cambio
    motivo = Column(String(255), nullable=True)  # Motivo del cambio de precio
    porcentaje_variacion = Column(Float, nullable=True)
    
    # Relación con el artículo
    articulo = relationship("Articulos", backref="historial_precios")