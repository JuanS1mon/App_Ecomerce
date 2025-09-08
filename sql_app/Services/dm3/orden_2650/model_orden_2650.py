# ============================================================================
# MODELO: ORDEN_2650
# ============================================================================
"""
Modelo para orden_2650
Parte del servicio: dm3
Módulo orden_2650 generado desde Editor Visual
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sql_app.db.database import Base
from datetime import datetime

class Orden2650(Base):
    """
    Modelo para orden_2650
    Módulo orden_2650 generado desde Editor Visual
    """
    __tablename__ = "orden_2650"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    numero_orden = Column(String(255))
    fecha_orden = Column(DateTime)
    total = Column(Integer)
    estado = Column(String(255))
    usuario_2650_id = Column(Integer, ForeignKey("usuario_2650.id"))

    def __repr__(self):
        return f"<Orden2650(id={self.id})">
