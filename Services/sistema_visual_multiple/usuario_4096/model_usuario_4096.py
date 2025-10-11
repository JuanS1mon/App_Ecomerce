# ============================================================================
# MODELO: USUARIO_4096
# ============================================================================
"""
Modelo para usuario_4096
Parte del servicio: sistema_visual_multiple
Módulo usuario_4096 generado desde Editor Visual
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from db.database import Base
from datetime import datetime

class Usuario4096(Base):
    """
    Modelo para usuario_4096
    Módulo usuario_4096 generado desde Editor Visual
    """
    __tablename__ = "usuario_4096"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(255))
    email = Column(String(255))
    telefono = Column(String(255))
    activo = Column(Boolean)

    def __repr__(self):
        return f"<Usuario4096(id={self.id})">
