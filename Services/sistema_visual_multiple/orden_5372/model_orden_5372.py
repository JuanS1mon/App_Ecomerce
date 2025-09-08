# ============================================================================
# MODELO: ORDEN_5372
# ============================================================================
"""
Modelo para orden_5372
Parte del servicio: sistema_visual_multiple
Módulo orden_5372 generado desde Editor Visual
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sql_app.db.database import Base
from datetime import datetime

class Orden5372(Base):
    """
    Modelo para orden_5372
    Módulo orden_5372 generado desde Editor Visual
    """
    __tablename__ = "orden_5372"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    numero_orden = Column(String(255))
    fecha_orden = Column(DateTime)
    total = Column(Integer)
    estado = Column(String(255))
    usuario_5372_id = Column(Integer, ForeignKey("usuario_5372.id"))

    def __repr__(self):
        return f"<Orden5372(id={self.id})">
