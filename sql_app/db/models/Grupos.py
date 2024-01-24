from sqlalchemy import Column, Integer, Float, String, DateTime
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Grupos(Base):
    __tablename__ = 'Grupos'
    Codigo = Column(Integer, primary_key=True)
    Descripcion = Column(String(50))
    DiasVencimiento = Column(Integer, primary_key=True)
    FechaProximoCorte = Column(DateTime)

from pydantic import BaseModel

class GruposModel(BaseModel):
    Codigo: int
    Descripcion: str
    DiasVencimiento: int
    FechaProximoCorte: datetime
