# ============================================================================
# MODELO: EMPRESAS
# ============================================================================
"""
Modelo para empresas
Parte del servicio: crm_empresarial
Empresas asociadas a los clientes
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sql_app.db.database import Base
from datetime import datetime

class Empresas(Base):
    """
    Modelo para empresas
    Empresas asociadas a los clientes
    """
    __tablename__ = "empresas"
    
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    nombre = Column(String(255), nullable=False)
    sector = Column(String(255))
    telefono = Column(String(255))
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    active = Column(Boolean, nullable=False)

    def __repr__(self):
        return f"<Empresas(id={self.id})">
