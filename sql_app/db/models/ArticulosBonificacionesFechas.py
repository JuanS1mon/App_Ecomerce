from sqlalchemy import Column, Integer, Float, String, DateTime
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Articulosbonificacionesfechas(Base):
    __tablename__ = 'ArticulosBonificacionesFechas'
    Articulo = Column(Integer, primary_key=True)
    Orden = Column(Integer, primary_key=True)
    Posicion = Column(Integer, primary_key=True)
    Detalle = Column(String(50))
    FechaInicio = Column(DateTime)
    FechaFin = Column(DateTime)

from pydantic import BaseModel

class ArticulosbonificacionesfechasModel(BaseModel):
    Articulo: int
    Orden: int
    Posicion: int
    Detalle: str
    FechaInicio: datetime
    FechaFin: datetime
