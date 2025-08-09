# ============================================================================
# MODELO: ORDENES
# ============================================================================
"""
Modelo para ordenes
Parte del servicio: ecommerce_app
Ordenes realizadas por los usuarios
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sql_app.db.database import Base
from datetime import datetime

class Ordenes(Base):
    """
    Modelo para ordenes
    Ordenes realizadas por los usuarios
    """
    __tablename__ = "ordenes"
    
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    usuario_id = Column(Integer, nullable=False, ForeignKey("usuarios.id"))
    fecha_orden = Column(DateTime, nullable=False)
    total = Column(Numeric, nullable=False)

    def __repr__(self):
        return f"<Ordenes(id={self.id})">
