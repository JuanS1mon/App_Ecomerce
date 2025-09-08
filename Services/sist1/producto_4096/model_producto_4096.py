# ============================================================================
# MODELO: PRODUCTO_4096
# ============================================================================
"""
Modelo para producto_4096
Parte del servicio: sist1
Módulo producto_4096 generado desde Editor Visual
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sql_app.db.database import Base
from datetime import datetime

class Producto4096(Base):
    """
    Modelo para producto_4096
    Módulo producto_4096 generado desde Editor Visual
    """
    __tablename__ = "producto_4096"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(255))
    precio = Column(Integer)
    stock = Column(Integer)
    categoria = Column(String(255))

    def __repr__(self):
        return f"<Producto4096(id={self.id})">
