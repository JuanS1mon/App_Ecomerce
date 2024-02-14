from sqlalchemy import Column, Integer, Float, String, DateTime
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Articuloscodigoprove(Base):
    __tablename__ = 'ArticulosCodigoProve'
    Articulo = Column(Integer, primary_key=True)
    Proveedor = Column(Integer, primary_key=True)
    Codigo = Column(String(50))
    FechaSincro = Column(DateTime)
    BonificacionUnidadesBase = Column(Integer, primary_key=True)
    BonificacionUnidadesCantidad = Column(Integer, primary_key=True)
    BonificacionUnidadesPosicion = Column(Integer, primary_key=True)

from pydantic import BaseModel

class ArticuloscodigoproveModel(BaseModel):
    Articulo: int
    Proveedor: int
    Codigo: str
    FechaSincro: datetime
    BonificacionUnidadesBase: int
    BonificacionUnidadesCantidad: int
    BonificacionUnidadesPosicion: int
