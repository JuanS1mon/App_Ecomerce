# ============================================================================
# MODELO: CATEGORIA_5372
# ============================================================================
"""
Modelo para categoria_5372
Parte del servicio: sistema_visual_multiple
Módulo categoria_5372 generado desde Editor Visual
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from db.database import Base
from datetime import datetime

class Categoria5372(Base):
    """
    Modelo para categoria_5372
    Módulo categoria_5372 generado desde Editor Visual
    """
    __tablename__ = "categoria_5372"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(255))
    descripcion = Column(String(255))
    activa = Column(Boolean)

    def __repr__(self):
        return f"<Categoria5372(id={self.id})">
