# ============================================================================
# MODELO: USUARIOS
# ============================================================================
"""
Modelo para usuarios
Parte del servicio: ecommerce_app
Tabla de usuarios registrados
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sql_app.db.database import Base
from datetime import datetime

class Usuarios(Base):
    """
    Modelo para usuarios
    Tabla de usuarios registrados
    """
    __tablename__ = "usuarios"
    
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    nombre = Column(String(100), nullable=False)
    email = Column(String(150), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    fecha_registro = Column(DateTime, nullable=False)

    def __repr__(self):
        return f"<Usuarios(id={self.id})">
