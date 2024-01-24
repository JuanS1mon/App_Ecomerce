from sqlalchemy import Column, Integer, Float, String, DateTime
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Cotizaciones(Base):
    __tablename__ = 'Cotizaciones'
    Cotizacion = Column(Integer, primary_key=True)
    Fecha = Column(DateTime)
    Descripcion = Column(String(50))
    Observacion = Column(String(50))
    PlazoEntrega = Column(Integer, primary_key=True)

from pydantic import BaseModel

class CotizacionesModel(BaseModel):
    Cotizacion: int
    Fecha: datetime
    Descripcion: str
    Observacion: str
    PlazoEntrega: int
