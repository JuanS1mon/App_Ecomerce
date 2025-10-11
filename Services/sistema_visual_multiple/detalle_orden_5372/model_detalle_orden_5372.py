# ============================================================================
# MODELO: DETALLE_ORDEN_5372
# ============================================================================
"""
Modelo para detalle_orden_5372
Parte del servicio: sistema_visual_multiple
Módulo detalle_orden_5372 generado desde Editor Visual
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from db.database import Base
from datetime import datetime

class DetalleOrden5372(Base):
    """
    Modelo para detalle_orden_5372
    Módulo detalle_orden_5372 generado desde Editor Visual
    """
    __tablename__ = "detalle_orden_5372"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    cantidad = Column(Integer)
    precio_unitario = Column(Integer)
    subtotal = Column(Integer)
    descuento = Column(Integer)
    orden_5372_id = Column(Integer, ForeignKey("orden_5372.id"))
    producto_5372_id = Column(Integer, ForeignKey("producto_5372.id"))

    def __repr__(self):
        return f"<DetalleOrden5372(id={self.id})">
