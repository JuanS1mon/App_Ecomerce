# ============================================================================
# MODELO: T
# ============================================================================
"""
Modelo para t
Parte del servicio: test_service
Tabla generada automáticamente
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sql_app.db.database import Base
from datetime import datetime

class T(Base):
    """
    Modelo para t
    Tabla generada automáticamente para test_service
    """
    __tablename__ = "t"
    
    id = Column(Integer, primary_key=True)

    def __repr__(self):
        return f"<T(id={self.id})">
