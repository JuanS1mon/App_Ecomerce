# ============================================================================
# MODELO: ORDEN_5862
# ============================================================================
"""
Modelo para orden_5862
Parte del servicio: sistema_visual_multiple
Módulo orden_5862 generado desde Editor Visual
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sql_app.db.database import Base
from datetime import datetime

class Orden5862(Base):
    """
    Modelo para orden_5862
    Módulo orden_5862 generado desde Editor Visual
    """
    __tablename__ = "orden_5862"
    
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    numero_orden = Column(String(255))
    fecha_orden = Column(DateTime)
    total = Column(Integer)
    estado = Column(String(255))
    id_usuario_5862 = Column(Integer, nullable=False, ForeignKey("usuario_5862.id"))

    def __repr__(self):
        return f"<Orden5862(id={self.id})">
