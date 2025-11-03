from sqlalchemy import Column, Integer, String, Boolean, Float, Date, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from db.database import Base

class EcomerceStock(Base):
    __tablename__ = 'ecomerce_stock'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_producto = Column(Integer, default=0)
    cantidad_disponible = Column(Integer, default=0)
    cantidad_reservada = Column(Integer, default=0)
    ubicacion = Column(String(255))
    updated_at = Column(DateTime, default=func.now())
