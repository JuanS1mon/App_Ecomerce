from sqlalchemy import Column, Integer, Float, String, DateTime
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Monedas(Base):
    __tablename__ = 'Monedas'
    Codigo = Column(Integer, primary_key=True)
    Descripcion = Column(String(50))
    Acumulador = Column(Integer, primary_key=True)
    Tipo = Column(String(50))
    DiasCobro = Column(Integer, primary_key=True)
    DescripcionImpresion = Column(String(50))
    MonedaCompletaRecargo = Column(Integer, primary_key=True)

from pydantic import BaseModel

class MonedasModel(BaseModel):
    Codigo: int
    Descripcion: str
    Acumulador: int
    Tipo: str
    DiasCobro: int
    DescripcionImpresion: str
    MonedaCompletaRecargo: int
