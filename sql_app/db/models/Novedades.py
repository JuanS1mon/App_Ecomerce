from sqlalchemy import Column, Integer, Float, String, DateTime
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Novedades(Base):
    __tablename__ = 'Novedades'
    Fecha = Column(DateTime)
    Sucursal = Column(Integer, primary_key=True)
    Articulo = Column(Integer, primary_key=True)
    Campo = Column(String(50))
    Hora = Column(String(50))
    Usuario = Column(Integer, primary_key=True)

from pydantic import BaseModel

class NovedadesModel(BaseModel):
    Fecha: datetime
    Sucursal: int
    Articulo: int
    Campo: str
    Hora: str
    Usuario: int
