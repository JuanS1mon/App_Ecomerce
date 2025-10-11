# ============================================================================
# MODELO: ORDEN_4096
# ============================================================================
"""
Modelo para orden_4096
Parte del servicio: sist1
Módulo orden_4096 generado desde Editor Visual
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from db.database import Base
from datetime import datetime

class Orden4096(Base):
    """
    Modelo para orden_4096
    Módulo orden_4096 generado desde Editor Visual
    """
    __tablename__ = "orden_4096"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    numero_orden = Column(String(255))
    fecha_orden = Column(DateTime)
    total = Column(Integer)
    estado = Column(String(255))
    usuario_4096_id = Column(Integer, ForeignKey("usuario_4096.id"))

    def __repr__(self):
        return f"<Orden4096(id={self.id})">
