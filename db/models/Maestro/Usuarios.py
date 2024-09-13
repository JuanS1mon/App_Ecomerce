from sqlalchemy import Column, Integer, Float, String, DateTime
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Modulos(Base):
    __tablename__ = 'Usuarios'
    Codigo = Column(Integer, primary_key=True)
    Modulo = Column(String(50))
    Ejecutable = Column(String(50))
    Descripcion = Column(String(50))

from pydantic import BaseModel

class ModulosModel(BaseModel):
    Codigo: int
    Modulo: str
    Ejecutable: str
    Descripcion: str
