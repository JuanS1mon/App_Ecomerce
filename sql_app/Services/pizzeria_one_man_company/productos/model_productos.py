# ============================================================================
# MODELO: PRODUCTOS
# ============================================================================
"""
Modelo para productos
Parte del servicio: pizzeria_one_man_company
Pizzas y productos vendibles. Precio de venta en centavos/pesos enteros, porción de costo calculable desde recetas.
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sql_app.db.database import Base
from datetime import datetime

class Productos(Base):
    """
    Modelo para productos
    Pizzas y productos vendibles. Precio de venta en centavos/pesos enteros, porción de costo calculable desde recetas.
    """
    __tablename__ = "productos"
    
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    codigo = Column(String(255), nullable=False)
    nombre = Column(String(255), nullable=False)
    descripcion = Column(String(255))
    precio_venta = Column(Integer, nullable=False)
    porciones = Column(Integer, nullable=False)
    activo = Column(Boolean, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime)

    def __repr__(self):
        return f"<Productos(id={self.id})">
