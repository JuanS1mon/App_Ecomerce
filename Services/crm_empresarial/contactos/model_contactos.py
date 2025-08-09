# ============================================================================
# MODELO: CONTACTOS
# ============================================================================
"""
Modelo para contactos
Parte del servicio: crm_empresarial
Contactos asociados a empresas y clientes
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sql_app.db.database import Base
from datetime import datetime

class Contactos(Base):
    """
    Modelo para contactos
    Contactos asociados a empresas y clientes
    """
    __tablename__ = "contactos"
    
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    id_empresa = Column(Integer, nullable=False)
    nombre = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    telefono = Column(String(255))
    cargo = Column(String(255))
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    active = Column(Boolean, nullable=False)

    def __repr__(self):
        return f"<Contactos(id={self.id})">
