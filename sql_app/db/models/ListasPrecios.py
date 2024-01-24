from sqlalchemy import Column, Integer, Float, String, DateTime
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Listasprecios(Base):
    __tablename__ = 'ListasPrecios'
    Lista = Column(Integer, primary_key=True)
    Fecha = Column(DateTime)
    Descripcion = Column(String(50))

from pydantic import BaseModel

class ListaspreciosModel(BaseModel):
    Lista: int
    Fecha: datetime
    Descripcion: str
