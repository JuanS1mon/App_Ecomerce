# ============================================================================
# MODELO: DETALLE_ORDEN_2650
# ============================================================================
"""
Modelo para detalle_orden_2650
Parte del servicio: dm3
Módulo detalle_orden_2650 generado desde Editor Visual
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sql_app.db.database import Base
from datetime import datetime

class DetalleOrden2650(Base):
    """
    Modelo para detalle_orden_2650
    Módulo detalle_orden_2650 generado desde Editor Visual
    """
    __tablename__ = "detalle_orden_2650"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    cantidad = Column(Integer)
    precio_unitario = Column(Integer)
    subtotal = Column(Integer)
    descuento = Column(Integer)
    orden_2650_id = Column(Integer, ForeignKey("orden_2650.id"))
    producto_2650_id = Column(Integer, ForeignKey("producto_2650.id"))

    def __repr__(self):
        return f"<DetalleOrden2650(id={self.id})">
