from sqlalchemy import Column, Integer, String, Boolean, Float, Date, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from ....db.database import Base

class Articulos(Base):
    __tablename__ = 'articulos'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    codigo = Column(String(255))
    descripcion = Column(String(255))
    preciocosto = Column(Float, default=0.0)
    precioventa = Column(Float, default=0.0)
    modelo = Column(String(255))
    marca = Column(String(255))
    id_tipo = Column(String(255))
    
    # Campos para códigos de barras y QR
    codigo_barras = Column(String(50), nullable=True, index=True)  # EAN, UPC u otro formato estándar
    codigo_barras_tipo = Column(String(20), nullable=True)  # EAN13, EAN8, CODE128, UPC, etc.
    qr_data = Column(Text, nullable=True)  # Datos almacenados en el QR (puede ser JSON)
    imagen_codigo_url = Column(String(255), nullable=True)  # Ruta de la imagen generada