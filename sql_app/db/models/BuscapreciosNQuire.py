from sqlalchemy import Column, Integer, Float, String, DateTime
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Buscapreciosnquire(Base):
    __tablename__ = 'BuscapreciosNQuire'
    Descripcion = Column(String(50))
    Marca = Column(Integer, primary_key=True)
    PresentacionUnidad = Column(String(50))

from pydantic import BaseModel

class BuscapreciosnquireModel(BaseModel):
    Descripcion: str
    Marca: int
    PresentacionUnidad: str
