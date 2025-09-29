# ============================================================================
# MODELO: DETALLE_ORDEN_7306
# ============================================================================
"""
Modelo para detalle_orden_7306
Parte del servicio: sistema_visual_multiple
Módulo detalle_orden_7306 generado desde Editor Visual
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sql_app.db.database import Base
from datetime import datetime

class DetalleOrden7306(Base):
    """
    Modelo para detalle_orden_7306
    Módulo detalle_orden_7306 generado desde Editor Visual
    """
    __tablename__ = "detalle_orden_7306"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    cantidad = Column(Integer)
    precio_unitario = Column(Integer)
    subtotal = Column(Integer)
    descuento = Column(Integer)
    orden_7306_id = Column(Integer, ForeignKey("orden_7306.id"))
    producto_7306_id = Column(Integer, ForeignKey("producto_7306.id"))

    def __repr__(self):
        return f"<DetalleOrden7306(id={self.id})">
