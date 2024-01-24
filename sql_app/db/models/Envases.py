from sqlalchemy import Column, Integer, Float, String, DateTime
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Envases(Base):
    __tablename__ = 'Envases'
    Codigo = Column(Integer, primary_key=True)
    Descripcion = Column(String(50))
    Orden = Column(Integer, primary_key=True)

from pydantic import BaseModel

class EnvasesModel(BaseModel):
    Codigo: int
    Descripcion: str
    Orden: int
