# ============================================================================
# MODELO: PRODUCTO_5862
# ============================================================================
"""
Modelo para producto_5862
Parte del servicio: sistema_visual_multiple
Módulo producto_5862 generado desde Editor Visual
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sql_app.db.database import Base
from datetime import datetime

class Producto5862(Base):
    """
    Modelo para producto_5862
    Módulo producto_5862 generado desde Editor Visual
    """
    __tablename__ = "producto_5862"
    
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    nombre = Column(String(255))
    precio = Column(Integer)
    stock = Column(Integer)
    categoria = Column(String(255))

    def __repr__(self):
        return f"<Producto5862(id={self.id})">
