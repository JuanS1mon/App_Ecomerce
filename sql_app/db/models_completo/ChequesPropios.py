from sqlalchemy import Column, Integer, Float, String, DateTime
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Chequespropios(Base):
    __tablename__ = 'ChequesPropios'
    Empresa = Column(Integer, primary_key=True)
    Banco = Column(Integer, primary_key=True)
    NroCheque = Column(Integer, primary_key=True)
    Estado = Column(String(50))
    FechaVencimiento = Column(DateTime)
    FechaEmision = Column(DateTime)
    TipoDestino = Column(String(50))
    CodigoDestino = Column(Integer, primary_key=True)
    CbteDestino = Column(Integer, primary_key=True)
    Detalle = Column(String(50))
    NroExtracto = Column(Integer, primary_key=True)

from pydantic import BaseModel

class ChequespropiosModel(BaseModel):
    Empresa: int
    Banco: int
    NroCheque: int
    Estado: str
    FechaVencimiento: datetime
    FechaEmision: datetime
    TipoDestino: str
    CodigoDestino: int
    CbteDestino: int
    Detalle: str
    NroExtracto: int
