from sqlalchemy import Column, Integer, String, Boolean, Float, Date, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from db.database import Base

class EcomercePedidos(Base):
    __tablename__ = 'ecomerce_pedidos'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_usuario = Column(Integer, default=0)
    fecha_pedido = Column(DateTime, default=func.now())
    total = Column(Integer, default=0)
    estado = Column(String(255))
