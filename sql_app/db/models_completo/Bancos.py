from sqlalchemy import Column, Integer, Float, String, DateTime
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Bancos(Base):
    __tablename__ = 'Bancos'
    Codigo = Column(Integer, primary_key=True)
    Descripcion = Column(String(50))
    CuentaBancaria = Column(String(50))
    Moneda = Column(Integer, primary_key=True)
    PuertoImpresionCheque = Column(String(50))
    CUIT = Column(String(50))
    ColorLetra = Column(Integer, primary_key=True)
    ColorFondo = Column(Integer, primary_key=True)
    PathArchivoPagos = Column(String(50))
    CBU = Column(String(50))

from pydantic import BaseModel

class BancosModel(BaseModel):
    Codigo: int
    Descripcion: str
    CuentaBancaria: str
    Moneda: int
    PuertoImpresionCheque: str
    CUIT: str
    ColorLetra: int
    ColorFondo: int
    PathArchivoPagos: str
    CBU: str
