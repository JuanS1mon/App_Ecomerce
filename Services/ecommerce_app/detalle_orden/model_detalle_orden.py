# ============================================================================
# MODELO: DETALLE_ORDEN
# ============================================================================
"""
Modelo para detalle_orden
Parte del servicio: ecommerce_app
Detalle de productos en cada orden
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sql_app.db.database import Base
from datetime import datetime

class DetalleOrden(Base):
    """
    Modelo para detalle_orden
    Detalle de productos en cada orden
    """
    __tablename__ = "detalle_orden"
    
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    orden_id = Column(Integer, nullable=False, ForeignKey("ordenes.id"))
    producto_id = Column(Integer, nullable=False, ForeignKey("productos.id"))
    cantidad = Column(Integer, nullable=False)
    precio_unitario = Column(Numeric, nullable=False)

    def __repr__(self):
        return f"<DetalleOrden(id={self.id})">
