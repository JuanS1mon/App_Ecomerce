from sqlalchemy import Column, Integer, Float, String, DateTime
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Subfamilias(Base):
    __tablename__ = 'SubFamilias'
    Codigo = Column(Integer, primary_key=True)
    Descripcion = Column(String(50))
    Familia = Column(Integer, primary_key=True)
    Transmitido = Column(Integer, primary_key=True)

from pydantic import BaseModel

class SubfamiliasModel(BaseModel):
    Codigo: int
    Descripcion: str
    Familia: int
    Transmitido: int
