# ============================================================================
# MODELO: DETALLE_ORDEN_5862
# ============================================================================
"""
Modelo para detalle_orden_5862
Parte del servicio: sistema_visual_multiple
Módulo detalle_orden_5862 generado desde Editor Visual
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sql_app.db.database import Base
from datetime import datetime

class DetalleOrden5862(Base):
    """
    Modelo para detalle_orden_5862
    Módulo detalle_orden_5862 generado desde Editor Visual
    """
    __tablename__ = "detalle_orden_5862"
    
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    cantidad = Column(Integer)
    precio_unitario = Column(Integer)
    subtotal = Column(Integer)
    descuento = Column(Integer)
    id_orden_5862 = Column(Integer, nullable=False, ForeignKey("orden_5862.id"))
    id_producto_5862 = Column(Integer, nullable=False, ForeignKey("producto_5862.id"))

    def __repr__(self):
        return f"<DetalleOrden5862(id={self.id})">
