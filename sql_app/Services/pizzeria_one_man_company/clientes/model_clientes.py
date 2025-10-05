# ============================================================================
# MODELO: CLIENTES
# ============================================================================
"""
Modelo para clientes
Parte del servicio: pizzeria_one_man_company
Clientes que realizan pedidos (puede ser anónimo / con teléfono o dirección para delivery)
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sql_app.db.database import Base
from datetime import datetime

class Clientes(Base):
    """
    Modelo para clientes
    Clientes que realizan pedidos (puede ser anónimo / con teléfono o dirección para delivery)
    """
    __tablename__ = "clientes"
    
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    nombre = Column(String(255))
    telefono = Column(String(255))
    direccion = Column(String(255))
    activo = Column(Boolean, nullable=False)
    created_at = Column(DateTime, nullable=False)

    def __repr__(self):
        return f"<Clientes(id={self.id})">
