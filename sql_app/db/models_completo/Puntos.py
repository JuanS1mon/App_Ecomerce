from sqlalchemy import Column, Integer, Float, String, DateTime
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Puntos(Base):
    __tablename__ = 'Puntos'
    Sucursal = Column(Integer, primary_key=True)
    Cliente = Column(Integer, primary_key=True)
    Fecha = Column(DateTime)
    TipoCbte = Column(String(50))
    PV = Column(Integer, primary_key=True)
    NroCbte = Column(Integer, primary_key=True)
    Puntos = Column(Integer, primary_key=True)

from pydantic import BaseModel

class PuntosModel(BaseModel):
    Sucursal: int
    Cliente: int
    Fecha: datetime
    TipoCbte: str
    PV: int
    NroCbte: int
    Puntos: int
