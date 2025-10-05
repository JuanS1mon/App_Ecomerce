# ============================================================================
# MODELO: USUARIOS
# ============================================================================
"""
Modelo para usuarios
Parte del servicio: pizzeria_one_man_company
Usuarios del sistema (propietario / operadores / agentes AI registrados)
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sql_app.db.database import Base
from datetime import datetime

class Usuarios(Base):
    """
    Modelo para usuarios
    Usuarios del sistema (propietario / operadores / agentes AI registrados)
    """
    __tablename__ = "usuarios"
    
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    nombre = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    rol = Column(String(255), nullable=False)
    activo = Column(Boolean, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime)

    def __repr__(self):
        return f"<Usuarios(id={self.id})">
