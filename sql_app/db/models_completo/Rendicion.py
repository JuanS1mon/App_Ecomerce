from sqlalchemy import Column, Integer, Float, String, DateTime
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Rendicion(Base):
    __tablename__ = 'Rendicion'
    Sucursal = Column(Integer, primary_key=True)
    NroMovimiento = Column(Integer, primary_key=True)
    Fecha = Column(DateTime)
    Cajero = Column(Integer, primary_key=True)
    Detalle = Column(String(50))
    TipoMovimiento = Column(Integer, primary_key=True)
    Empresa = Column(Integer, primary_key=True)
    Tipo = Column(String(50))
    FechaDesde = Column(DateTime)
    FechaHasta = Column(DateTime)
    Observacion = Column(String(50))

from pydantic import BaseModel

class RendicionModel(BaseModel):
    Sucursal: int
    NroMovimiento: int
    Fecha: datetime
    Cajero: int
    Detalle: str
    TipoMovimiento: int
    Empresa: int
    Tipo: str
    FechaDesde: datetime
    FechaHasta: datetime
    Observacion: str
