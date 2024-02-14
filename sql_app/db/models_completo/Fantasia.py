from sqlalchemy import Column, Integer, Float, String, DateTime
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Fantasia(Base):
    __tablename__ = 'Fantasia'
    Sucursal = Column(Integer, primary_key=True)
    Linea = Column(Integer, primary_key=True)
    Texto = Column(String(50))

from pydantic import BaseModel

class FantasiaModel(BaseModel):
    Sucursal: int
    Linea: int
    Texto: str
