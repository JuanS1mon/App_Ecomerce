# ============================================================================
# MODELO: RECETAS
# ============================================================================
"""
Modelo para recetas
Parte del servicio: pizzeria_one_man_company
Mapping producto ↔ ingrediente: cantidad de ingrediente por unidad de producto (ej: gramos por pizza). Permite calcular costo por producto.
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sql_app.db.database import Base
from datetime import datetime

class Recetas(Base):
    """
    Modelo para recetas
    Mapping producto ↔ ingrediente: cantidad de ingrediente por unidad de producto (ej: gramos por pizza). Permite calcular costo por producto.
    """
    __tablename__ = "recetas"
    
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    id_producto = Column(Integer, nullable=False)
    id_ingrediente = Column(Integer, nullable=False)
    cantidad = Column(Integer, nullable=False)
    unidad = Column(String(255), nullable=False)
    nota = Column(String(255))

    def __repr__(self):
        return f"<Recetas(id={self.id})">
