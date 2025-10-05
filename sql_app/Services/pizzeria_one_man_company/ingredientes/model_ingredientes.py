# ============================================================================
# MODELO: INGREDIENTES
# ============================================================================
"""
Modelo para ingredientes
Parte del servicio: pizzeria_one_man_company
Ingredientes con costo unitario y stock para calcular costo de receta y optimizar compras.
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sql_app.db.database import Base
from datetime import datetime

class Ingredientes(Base):
    """
    Modelo para ingredientes
    Ingredientes con costo unitario y stock para calcular costo de receta y optimizar compras.
    """
    __tablename__ = "ingredientes"
    
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    nombre = Column(String(255), nullable=False)
    unidad_medida = Column(String(255), nullable=False)
    costo_unitario = Column(Integer, nullable=False)
    stock_unidades = Column(Integer, nullable=False)
    punto_reorden = Column(Integer, nullable=False)
    activo = Column(Boolean, nullable=False)
    updated_at = Column(DateTime)

    def __repr__(self):
        return f"<Ingredientes(id={self.id})">
