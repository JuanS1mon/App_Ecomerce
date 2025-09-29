# ============================================================================
# MODELO: CATEGORIA_7306
# ============================================================================
"""
Modelo para categoria_7306
Parte del servicio: sistema_visual_multiple
Módulo categoria_7306 generado desde Editor Visual
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sql_app.db.database import Base
from datetime import datetime

class Categoria7306(Base):
    """
    Modelo para categoria_7306
    Módulo categoria_7306 generado desde Editor Visual
    """
    __tablename__ = "categoria_7306"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(255))
    descripcion = Column(String(255))
    activa = Column(Boolean)

    def __repr__(self):
        return f"<Categoria7306(id={self.id})">
