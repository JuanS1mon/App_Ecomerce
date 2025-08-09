# ============================================================================
# MODELO: CLIENTES
# ============================================================================
"""
Modelo para clientes
Parte del servicio: crm_empresarial
Tabla de clientes individuales o corporativos
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sql_app.db.database import Base
from datetime import datetime

class Clientes(Base):
    """
    Modelo para clientes
    Tabla de clientes individuales o corporativos
    """
    __tablename__ = "clientes"
    
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    nombre = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    telefono = Column(String(255))
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    active = Column(Boolean, nullable=False)

    def __repr__(self):
        return f"<Clientes(id={self.id})">
