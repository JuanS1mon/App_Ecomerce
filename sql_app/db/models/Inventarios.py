from sqlalchemy import Column, Integer, Float, String, DateTime
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Inventarios(Base):
    __tablename__ = 'Inventarios'
    Sucursal = Column(Integer, primary_key=True)
    Inventario = Column(Integer, primary_key=True)
    Fecha = Column(DateTime)
    Descripcion = Column(String(50))

from pydantic import BaseModel

class InventariosModel(BaseModel):
    Sucursal: int
    Inventario: int
    Fecha: datetime
    Descripcion: str
