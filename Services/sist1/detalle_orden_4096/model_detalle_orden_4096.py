# ============================================================================
# MODELO: DETALLE_ORDEN_4096
# ============================================================================
"""
Modelo para detalle_orden_4096
Parte del servicio: sist1
Módulo detalle_orden_4096 generado desde Editor Visual
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from db.database import Base
from datetime import datetime

class DetalleOrden4096(Base):
    """
    Modelo para detalle_orden_4096
    Módulo detalle_orden_4096 generado desde Editor Visual
    """
    __tablename__ = "detalle_orden_4096"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    cantidad = Column(Integer)
    precio_unitario = Column(Integer)
    subtotal = Column(Integer)
    descuento = Column(Integer)
    orden_4096_id = Column(Integer, ForeignKey("orden_4096.id"))
    producto_4096_id = Column(Integer, ForeignKey("producto_4096.id"))

    def __repr__(self):
        return f"<DetalleOrden4096(id={self.id})">
