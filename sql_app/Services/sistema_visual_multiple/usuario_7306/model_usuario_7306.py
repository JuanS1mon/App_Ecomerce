# ============================================================================
# MODELO: USUARIO_7306
# ============================================================================
"""
Modelo para usuario_7306
Parte del servicio: sistema_visual_multiple
Módulo usuario_7306 generado desde Editor Visual
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sql_app.db.database import Base
from datetime import datetime

class Usuario7306(Base):
    """
    Modelo para usuario_7306
    Módulo usuario_7306 generado desde Editor Visual
    """
    __tablename__ = "usuario_7306"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(255))
    email = Column(String(255))
    telefono = Column(String(255))
    activo = Column(Boolean)

    def __repr__(self):
        return f"<Usuario7306(id={self.id})">
