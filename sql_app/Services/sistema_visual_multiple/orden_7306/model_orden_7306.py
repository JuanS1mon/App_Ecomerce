# ============================================================================
# MODELO: ORDEN_7306
# ============================================================================
"""
Modelo para orden_7306
Parte del servicio: sistema_visual_multiple
Módulo orden_7306 generado desde Editor Visual
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sql_app.db.database import Base
from datetime import datetime

class Orden7306(Base):
    """
    Modelo para orden_7306
    Módulo orden_7306 generado desde Editor Visual
    """
    __tablename__ = "orden_7306"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    numero_orden = Column(String(255))
    fecha_orden = Column(DateTime)
    total = Column(Integer)
    estado = Column(String(255))
    usuario_7306_id = Column(Integer, ForeignKey("usuario_7306.id"))

    def __repr__(self):
        return f"<Orden7306(id={self.id})">
