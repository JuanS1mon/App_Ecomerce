from sqlalchemy import Column, Integer, Float, String, DateTime
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Encabezado(Base):
    __tablename__ = 'Encabezado'
    Linea = Column(Integer, primary_key=True)
    Texto = Column(String(50))
    Sucursal = Column(Integer, primary_key=True)

from pydantic import BaseModel

class EncabezadoModel(BaseModel):
    Linea: int
    Texto: str
    Sucursal: int
