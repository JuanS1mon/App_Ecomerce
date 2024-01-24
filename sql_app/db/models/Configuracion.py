from sqlalchemy import Column, Integer, Float, String, DateTime
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Configuracion(Base):
    __tablename__ = 'Configuracion'
    Sucursal = Column(Integer, primary_key=True)
    CuentaCobranza = Column(String(50))
    Modo = Column(String(50))
    PuertoRecibo = Column(String(50))
    PuertoListados = Column(String(50))
    LineasPorPagina = Column(Integer, primary_key=True)

from pydantic import BaseModel

class ConfiguracionModel(BaseModel):
    Sucursal: int
    CuentaCobranza: str
    Modo: str
    PuertoRecibo: str
    PuertoListados: str
    LineasPorPagina: int
