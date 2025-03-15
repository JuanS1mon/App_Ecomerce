from sqlalchemy import Column, Integer, String, Boolean, Float
from ..database import Base

class Articulos(Base):
    __tablename__ = 'articulos'

    id = Column(Integer, primary_key=True, index=True, default=0)
    codigo = Column(String(50), default=' ')
    descripcion = Column(String(50), default=' ')
    precio_costo = Column(Float, default=0.0)
    modelo = Column(String(50), default=' ')
    marca = Column(String(50), default=' ')
    id_tipo = Column(Integer, primary_key=True, index=True, default=0)
