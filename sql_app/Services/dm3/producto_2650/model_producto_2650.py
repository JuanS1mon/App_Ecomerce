# ============================================================================
# MODELO: PRODUCTO_2650
# ============================================================================
"""
Modelo para producto_2650
Parte del servicio: dm3
Módulo producto_2650 generado desde Editor Visual
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sql_app.db.database import Base
from datetime import datetime

class Producto2650(Base):
    """
    Modelo para producto_2650
    Módulo producto_2650 generado desde Editor Visual
    """
    __tablename__ = "producto_2650"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(255))
    precio = Column(Integer)
    stock = Column(Integer)
    categoria = Column(String(255))

    def __repr__(self):
        return f"<Producto2650(id={self.id})">
