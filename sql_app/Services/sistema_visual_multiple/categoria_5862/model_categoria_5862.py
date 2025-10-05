# ============================================================================
# MODELO: CATEGORIA_5862
# ============================================================================
"""
Modelo para categoria_5862
Parte del servicio: sistema_visual_multiple
Módulo categoria_5862 generado desde Editor Visual
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sql_app.db.database import Base
from datetime import datetime

class Categoria5862(Base):
    """
    Modelo para categoria_5862
    Módulo categoria_5862 generado desde Editor Visual
    """
    __tablename__ = "categoria_5862"
    
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    nombre = Column(String(255))
    descripcion = Column(String(255))
    activa = Column(Boolean)

    def __repr__(self):
        return f"<Categoria5862(id={self.id})">
