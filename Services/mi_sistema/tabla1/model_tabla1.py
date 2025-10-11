# ============================================================================
# MODELO: TABLA1
# ============================================================================
"""
Modelo para tabla1
Parte del servicio: mi_sistema
Tabla generada automáticamente
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from db.database import Base
from datetime import datetime

class Tabla1(Base):
    """
    Modelo para tabla1
    Tabla generada automáticamente para mi_sistema
    """
    __tablename__ = "tabla1"
    
    id = Column(Integer, primary_key=True, autoincrement=True)

    def __repr__(self):
        return f"<Tabla1(id={self.id})">
