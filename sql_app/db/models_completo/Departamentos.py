from sqlalchemy import Column, Integer, Float, String, DateTime
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Departamentos(Base):
    __tablename__ = 'Departamentos'
    Codigo = Column(Integer, primary_key=True)
    Descripcion = Column(String(50))
    Acumulador = Column(Integer, primary_key=True)
    IVA = Column(Integer, primary_key=True)
    DescripcionImpresion = Column(String(50))
    Orden = Column(Integer, primary_key=True)
    Clase = Column(Integer, primary_key=True)
    Sector = Column(Integer, primary_key=True)

from pydantic import BaseModel

class DepartamentosModel(BaseModel):
    Codigo: int
    Descripcion: str
    Acumulador: int
    IVA: int
    DescripcionImpresion: str
    Orden: int
    Clase: int
    Sector: int
