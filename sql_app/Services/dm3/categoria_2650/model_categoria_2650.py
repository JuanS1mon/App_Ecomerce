# ============================================================================
# MODELO: CATEGORIA_2650
# ============================================================================
"""
Modelo para categoria_2650
Parte del servicio: dm3
Módulo categoria_2650 generado desde Editor Visual
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sql_app.db.database import Base
from datetime import datetime

class Categoria2650(Base):
    """
    Modelo para categoria_2650
    Módulo categoria_2650 generado desde Editor Visual
    """
    __tablename__ = "categoria_2650"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(255))
    descripcion = Column(String(255))
    activa = Column(Boolean)

    def __repr__(self):
        return f"<Categoria2650(id={self.id})">
