from sqlalchemy import Column, Integer, Float, String, DateTime
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Inventariosarticulos(Base):
    __tablename__ = 'InventariosArticulos'
    Fecha = Column(DateTime)
    Sucursal = Column(Integer, primary_key=True)
    Inventario = Column(Integer, primary_key=True)
    Articulo = Column(Integer, primary_key=True)
    FechaCarga = Column(DateTime)

from pydantic import BaseModel

class InventariosarticulosModel(BaseModel):
    Fecha: datetime
    Sucursal: int
    Inventario: int
    Articulo: int
    FechaCarga: datetime
