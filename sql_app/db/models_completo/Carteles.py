from sqlalchemy import Column, Integer, Float, String, DateTime
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Carteles(Base):
    __tablename__ = 'Carteles'
    Cartel = Column(Integer, primary_key=True)
    Fecha = Column(DateTime)
    Color = Column(Integer, primary_key=True)
    X = Column(Integer, primary_key=True)
    Y = Column(Integer, primary_key=True)
    Alto = Column(Integer, primary_key=True)
    Ancho = Column(Integer, primary_key=True)
    Texto = Column(String(50))
    Usuario = Column(Integer, primary_key=True)
    FechaFin = Column(DateTime)

from pydantic import BaseModel

class CartelesModel(BaseModel):
    Cartel: int
    Fecha: datetime
    Color: int
    X: int
    Y: int
    Alto: int
    Ancho: int
    Texto: str
    Usuario: int
    FechaFin: datetime
