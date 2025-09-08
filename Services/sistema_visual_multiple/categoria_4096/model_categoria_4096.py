# ============================================================================
# MODELO: CATEGORIA_4096
# ============================================================================
"""
Modelo para categoria_4096
Parte del servicio: sistema_visual_multiple
Módulo categoria_4096 generado desde Editor Visual
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sql_app.db.database import Base
from datetime import datetime

class Categoria4096(Base):
    """
    Modelo para categoria_4096
    Módulo categoria_4096 generado desde Editor Visual
    """
    __tablename__ = "categoria_4096"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(255))
    descripcion = Column(String(255))
    activa = Column(Boolean)

    def __repr__(self):
        return f"<Categoria4096(id={self.id})">
