from sqlalchemy import Column, Integer, Float, String, DateTime
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Tablaimpuestos(Base):
    __tablename__ = 'TablaImpuestos'
    Codigo = Column(Integer, primary_key=True)
    Descripcion = Column(String(50))
    TipoImpuesto = Column(String(50))
    TipoDetalle = Column(String(50))

from pydantic import BaseModel

class TablaimpuestosModel(BaseModel):
    Codigo: int
    Descripcion: str
    TipoImpuesto: str
    TipoDetalle: str
