from sqlalchemy import Column, Integer, String, Boolean, Float, Date, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from db.database import Base

class EcomerceProductos(Base):
    __tablename__ = 'ecomerce_productos'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    codigo = Column(String(255))
    nombre = Column(String(255))
    descripcion = Column(String(255))
    id_categoria = Column(Integer, default=0)
    precio = Column(Integer, default=0)
    imagen_url = Column(String(255))
    active = Column(Boolean, default=False)

class EcomerceProductVariants(Base):
    __tablename__ = 'ecomerce_product_variants'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('ecomerce_productos.id'), nullable=False)
    color = Column(String(100), nullable=True)
    tipo = Column(String(100), nullable=True)  # ej: con cable, sin cable
    precio_adicional = Column(Integer, default=0)
    stock = Column(Integer, default=0)
    imagen_url = Column(String(255), nullable=True)
    active = Column(Boolean, default=True)
