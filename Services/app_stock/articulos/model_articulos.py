from sqlalchemy import Column, Integer, String, Boolean, Float, Date, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from db.database import Base

class Articulos(Base):
    __tablename__ = 'articulos'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    codigo = Column(String(255))
    descripcion = Column(String(255))
    preciocosto = Column(Float, default=0.0)
    modelo = Column(String(255))
    marca = Column(String(255))
    id_tipo = Column(String(255))
