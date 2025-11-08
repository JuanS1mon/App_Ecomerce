from sqlalchemy import Column, Integer, String, Boolean, Float, Date, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from db.database import Base

class EcomercePedidos(Base):
    __tablename__ = 'ecomerce_pedidos'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_usuario = Column(Integer, default=0)
    fecha_pedido = Column(DateTime, default=func.now())
    total = Column(Float, default=0.0)
    estado = Column(String(255))
    metodo_pago = Column(String(50), default='efectivo')  # efectivo, mercadopago, presupuesto
    external_reference = Column(String(255), nullable=True)  # Para MercadoPago
