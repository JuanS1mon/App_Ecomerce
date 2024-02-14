from sqlalchemy import Column, Integer, Float, String, DateTime
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Articulossucursales(Base):
    __tablename__ = 'ArticulosSucursales'
    Articulo = Column(Integer, primary_key=True)
    Sucursal = Column(Integer, primary_key=True)
    Gondola = Column(String(50))
    Ruteo = Column(String(50))
    Bulto = Column(Integer, primary_key=True)
    CantidadEtiquetas = Column(Integer, primary_key=True)
    ModeloEtiqueta = Column(String(50))
    FechaSincro = Column(DateTime)

from pydantic import BaseModel

class ArticulossucursalesModel(BaseModel):
    Articulo: int
    Sucursal: int
    Gondola: str
    Ruteo: str
    Bulto: int
    CantidadEtiquetas: int
    ModeloEtiqueta: str
    FechaSincro: datetime
