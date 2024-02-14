from sqlalchemy import Column, Integer, Float, String, DateTime
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Tiposmovimientos(Base):
    __tablename__ = 'TiposMovimientos'
    Codigo = Column(Integer, primary_key=True)
    Descripcion = Column(String(50))
    Tipo = Column(String(50))

from pydantic import BaseModel

class TiposmovimientosModel(BaseModel):
    Codigo: int
    Descripcion: str
    Tipo: str
