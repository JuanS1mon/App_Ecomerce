from sqlalchemy import Column, Integer, Float, String, DateTime
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Chequeterceros(Base):
    __tablename__ = 'ChequeTerceros'
    Empresa = Column(Integer, primary_key=True)
    Cliente = Column(Integer, primary_key=True)
    Emisor = Column(String(50))
    Banco = Column(String(50))
    FechaVencimiento = Column(DateTime)
    FechaEmision = Column(DateTime)
    FechaRecepcion = Column(DateTime)
    FechaEntrega = Column(DateTime)
    TipoDestino = Column(String(50))
    CodigoDestino = Column(Integer, primary_key=True)
    CbteDestino = Column(Integer, primary_key=True)
    Detalle = Column(String(50))
    TipoOrigen = Column(String(50))
    CodigoOrigen = Column(Integer, primary_key=True)
    Sucursal = Column(Integer, primary_key=True)
    OrdenCarga = Column(Integer, primary_key=True)
    ClearingHoras = Column(Integer, primary_key=True)

from pydantic import BaseModel

class ChequetercerosModel(BaseModel):
    Empresa: int
    Cliente: int
    Emisor: str
    Banco: str
    FechaVencimiento: datetime
    FechaEmision: datetime
    FechaRecepcion: datetime
    FechaEntrega: datetime
    TipoDestino: str
    CodigoDestino: int
    CbteDestino: int
    Detalle: str
    TipoOrigen: str
    CodigoOrigen: int
    Sucursal: int
    OrdenCarga: int
    ClearingHoras: int
