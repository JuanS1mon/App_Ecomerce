# ============================================================================
# MODELO: PRODUCTOS
# ============================================================================
"""
Modelo para productos
Parte del servicio: ecommerce_app
Catalogo de productos disponibles
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sql_app.db.database import Base
from datetime import datetime

class Productos(Base):
    """
    Modelo para productos
    Catalogo de productos disponibles
    """
    __tablename__ = "productos"
    
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    nombre = Column(String(200), nullable=False)
    descripcion = Column(Text)
    precio = Column(Numeric, nullable=False)
    stock = Column(Integer, nullable=False)

    def __repr__(self):
        return f"<Productos(id={self.id})">
