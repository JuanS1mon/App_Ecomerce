from sqlalchemy import Column, Integer, Float, String, DateTime
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Familias(Base):
    __tablename__ = 'Familias'
    Codigo = Column(Integer, primary_key=True)
    Descripcion = Column(String(50))
    Departamento = Column(Integer, primary_key=True)

from pydantic import BaseModel

class FamiliasModel(BaseModel):
    Codigo: int
    Descripcion: str
    Departamento: int
