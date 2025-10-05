# ============================================================================
# MODELO: PEDIDOS
# ============================================================================
"""
Modelo para pedidos
Parte del servicio: pizzeria_one_man_company
Pedidos de clientes. Contiene resumen del pedido; los items pueden deserializarse desde 'items_json' para mantener la estructura simple en una app one-man. (Si se prefiere, se puede agregar tabla 'pedido_items' más tarde.)
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sql_app.db.database import Base
from datetime import datetime

class Pedidos(Base):
    """
    Modelo para pedidos
    Pedidos de clientes. Contiene resumen del pedido; los items pueden deserializarse desde 'items_json' para mantener la estructura simple en una app one-man. (Si se prefiere, se puede agregar tabla 'pedido_items' más tarde.)
    """
    __tablename__ = "pedidos"
    
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    id_usuario = Column(Integer, nullable=False)
    id_cliente = Column(Integer)
    items_json = Column(String(255), nullable=False)
    subtotal = Column(Integer, nullable=False)
    descuento = Column(Integer)
    total = Column(Integer, nullable=False)
    metodo_pago = Column(String(255), nullable=False)
    estado = Column(String(255), nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime)

    def __repr__(self):
        return f"<Pedidos(id={self.id})">
