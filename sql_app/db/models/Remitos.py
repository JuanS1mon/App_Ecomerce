from sqlalchemy import Column, Integer, Float, String, DateTime
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Remitos(Base):
    __tablename__ = 'Remitos'
    Fecha = Column(DateTime)
    Sucursal = Column(Integer, primary_key=True)
    Remito = Column(Integer, primary_key=True)
    TipoOrigenDestino = Column(String(50))
    CodigoOrigenDestino = Column(Integer, primary_key=True)
    Concepto = Column(Integer, primary_key=True)
    Detalle = Column(String(50))
    OrdenCompra = Column(Integer, primary_key=True)
    Pedido = Column(Integer, primary_key=True)
    OrdenProduccion = Column(Integer, primary_key=True)
    Usuario = Column(Integer, primary_key=True)

from pydantic import BaseModel

class RemitosModel(BaseModel):
    Fecha: datetime
    Sucursal: int
    Remito: int
    TipoOrigenDestino: str
    CodigoOrigenDestino: int
    Concepto: int
    Detalle: str
    OrdenCompra: int
    Pedido: int
    OrdenProduccion: int
    Usuario: int
