from sqlalchemy import Column, Integer, Float, String, DateTime
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Articulosbonificaciones(Base):
    __tablename__ = 'ArticulosBonificaciones'
    Articulo = Column(Integer, primary_key=True)
    Posicion = Column(Integer, primary_key=True)
    Detalle = Column(String(50))
    FechaSincro = Column(DateTime)

from pydantic import BaseModel

class ArticulosbonificacionesModel(BaseModel):
    Articulo: int
    Posicion: int
    Detalle: str
    FechaSincro: datetime
