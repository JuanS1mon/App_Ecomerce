# ============================================================================
# MODELO: USUARIO_5372
# ============================================================================
"""
Modelo para usuario_5372
Parte del servicio: sistema_visual_multiple
Módulo usuario_5372 generado desde Editor Visual
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sql_app.db.database import Base
from datetime import datetime

class Usuario5372(Base):
    """
    Modelo para usuario_5372
    Módulo usuario_5372 generado desde Editor Visual
    """
    __tablename__ = "usuario_5372"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(255))
    email = Column(String(255))
    telefono = Column(String(255))
    activo = Column(Boolean)

    def __repr__(self):
        return f"<Usuario5372(id={self.id})">
