from sqlalchemy import Column, Integer, Float, String, DateTime
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Localidades(Base):
    __tablename__ = 'Localidades'
    Codigo = Column(Integer, primary_key=True)
    Descripcion = Column(String(50))
    Provincia = Column(Integer, primary_key=True)
    CodigoPostal = Column(String(50))
    CondicionFiscal = Column(Integer, primary_key=True)

from pydantic import BaseModel

class LocalidadesModel(BaseModel):
    Codigo: int
    Descripcion: str
    Provincia: int
    CodigoPostal: str
    CondicionFiscal: int
