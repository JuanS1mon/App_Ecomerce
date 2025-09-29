# ============================================================================
# MODELO: PRODUCTO_7306
# ============================================================================
"""
Modelo para producto_7306
Parte del servicio: sistema_visual_multiple
Módulo producto_7306 generado desde Editor Visual
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sql_app.db.database import Base
from datetime import datetime

class Producto7306(Base):
    """
    Modelo para producto_7306
    Módulo producto_7306 generado desde Editor Visual
    """
    __tablename__ = "producto_7306"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(255))
    precio = Column(Integer)
    stock = Column(Integer)
    categoria = Column(String(255))

    def __repr__(self):
        return f"<Producto7306(id={self.id})">
