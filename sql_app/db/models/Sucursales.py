from sqlalchemy import Column, Integer, Float, String, DateTime
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Sucursales(Base):
    __tablename__ = 'Sucursales'
    Codigo = Column(Integer, primary_key=True)
    Descripcion = Column(String(50))
    Tipo = Column(String(50))
    Direccion = Column(String(50))
    Telefono = Column(String(50))
    Email = Column(String(50))
    Paginaweb = Column(String(50))
    StockCentral = Column(Integer, primary_key=True)
    DestinoNovedad = Column(String(50))
    Empresa = Column(Integer, primary_key=True)
    ReservaDeSucursal = Column(Integer, primary_key=True)
    CliRangoDesde = Column(Integer, primary_key=True)
    CliRangoHasta = Column(Integer, primary_key=True)
    StoredIDMP = Column(String(50))

from pydantic import BaseModel

class SucursalesModel(BaseModel):
    Codigo: int
    Descripcion: str
    Tipo: str
    Direccion: str
    Telefono: str
    Email: str
    Paginaweb: str
    StockCentral: int
    DestinoNovedad: str
    Empresa: int
    ReservaDeSucursal: int
    CliRangoDesde: int
    CliRangoHasta: int
    StoredIDMP: str
