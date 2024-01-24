from sqlalchemy import Column, Integer, Float, String, DateTime
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Zonas(Base):
    __tablename__ = 'Zonas'
    Codigo = Column(Integer, primary_key=True)
    Descripcion = Column(String(50))

from pydantic import BaseModel

class ZonasModel(BaseModel):
    Codigo: int
    Descripcion: str
