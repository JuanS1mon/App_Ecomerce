from sqlalchemy import Column, Integer, Float, String, DateTime
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Articulospreciosrangos(Base):
    __tablename__ = 'ArticulosPreciosRangos'
    Articulo = Column(Integer, primary_key=True)
    CantidadDesde = Column(Integer, primary_key=True)
    CantidadHasta = Column(Integer, primary_key=True)
    TipoValor = Column(String(50))
    FechaSincro = Column(DateTime)

from pydantic import BaseModel

class ArticulospreciosrangosModel(BaseModel):
    Articulo: int
    CantidadDesde: int
    CantidadHasta: int
    TipoValor: str
    FechaSincro: datetime
