from sqlalchemy import Column, Integer, Float, String, DateTime
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Cajas(Base):
    __tablename__ = 'Cajas'
    Sucursal = Column(Integer, primary_key=True)
    Caja = Column(Integer, primary_key=True)
    PuntoVenta = Column(Integer, primary_key=True)
    Estado = Column(String(50))
    PuertoComunica = Column(String(50))
    PuertoArchivo = Column(String(50))
    Direccion = Column(String(50))
    Empresa = Column(Integer, primary_key=True)

from pydantic import BaseModel

class CajasModel(BaseModel):
    Sucursal: int
    Caja: int
    PuntoVenta: int
    Estado: str
    PuertoComunica: str
    PuertoArchivo: str
    Direccion: str
    Empresa: int
