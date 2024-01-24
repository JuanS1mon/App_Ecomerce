from sqlalchemy import Column, Integer, Float, String, DateTime
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Agrupados(Base):
    __tablename__ = 'Agrupados'
    Grupo = Column(Integer, primary_key=True)
    Tipo = Column(String(50))
    Descripcion = Column(String(50))

from pydantic import BaseModel

class AgrupadosModel(BaseModel):
    Grupo: int
    Tipo: str
    Descripcion: str
