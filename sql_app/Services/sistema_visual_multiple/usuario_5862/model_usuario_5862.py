# ============================================================================
# MODELO: USUARIO_5862
# ============================================================================
"""
Modelo para usuario_5862
Parte del servicio: sistema_visual_multiple
Módulo usuario_5862 generado desde Editor Visual
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sql_app.db.database import Base
from datetime import datetime

class Usuario5862(Base):
    """
    Modelo para usuario_5862
    Módulo usuario_5862 generado desde Editor Visual
    """
    __tablename__ = "usuario_5862"
    
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    nombre = Column(String(255))
    email = Column(String(255))
    telefono = Column(String(255))
    activo = Column(Boolean)

    def __repr__(self):
        return f"<Usuario5862(id={self.id})">
