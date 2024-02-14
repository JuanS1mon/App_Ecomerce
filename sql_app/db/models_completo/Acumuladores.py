from sqlalchemy import Column, Integer, Float, String, DateTime
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Acumuladores(Base):
    __tablename__ = 'Acumuladores'
    Codigo = Column(Integer, primary_key=True)
    Descripcion = Column(String(50))
    Tipo = Column(String(50))
    Acumulador = Column(Integer, primary_key=True)
    Moneda = Column(Integer, primary_key=True)

from pydantic import BaseModel

class AcumuladoresModel(BaseModel):
    Codigo: int
    Descripcion: str
    Tipo: str
    Acumulador: int
    Moneda: int
