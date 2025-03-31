from sqlalchemy import Column, Integer, String, Boolean, Float, Date, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from db.database import Base

class Articulos(Base):
    __tablename__ = 'articulos'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    codigo = Column(String(255))
    descripcion = Column(String(255))
    precio_costo = Column(Float, default=0.0)
    modelo = Column(String(255))
    marca = Column(Integer, default=0)
    id_tipo = Column(Integer, default=0)
