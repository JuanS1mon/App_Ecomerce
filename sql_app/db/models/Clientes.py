from sqlalchemy import Column, Integer, Float, String, DateTime
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Clientes(Base):
    __tablename__ = 'Clientes'
    Sucursal = Column(Integer, primary_key=True)
    Codigo = Column(Integer, primary_key=True)
    Grupo = Column(Integer, primary_key=True)
    Nombre = Column(String(50))
    RazonSocial = Column(String(50))
    Categoria = Column(Integer, primary_key=True)
    TipoIva = Column(String(50))
    Documento = Column(String(50))
    FechaVencTarjeta = Column(DateTime)
    FechaAlta = Column(DateTime)
    Estado = Column(String(50))
    IIBB = Column(String(50))
    Vendedor = Column(Integer, primary_key=True)
    FormaPago = Column(Integer, primary_key=True)
    ListaPrecio = Column(Integer, primary_key=True)
    TipoDocumento = Column(Integer, primary_key=True)
    Repartidor = Column(Integer, primary_key=True)
    Cobrador = Column(Integer, primary_key=True)
    Rubro = Column(Integer, primary_key=True)
    Observacion = Column(String(50))
    VtoCUIT = Column(DateTime)
    Abasto = Column(Integer, primary_key=True)
    OrdenZona = Column(Integer, primary_key=True)
    DiasToleranciaVto = Column(Integer, primary_key=True)
    Clave = Column(String(50))
    TipoPeriodo = Column(String(50))

from pydantic import BaseModel

class ClientesModel(BaseModel):
    Sucursal: int
    Codigo: int
    Grupo: int
    Nombre: str
    RazonSocial: str
    Categoria: int
    TipoIva: str
    Documento: str
    FechaVencTarjeta: datetime
    FechaAlta: datetime
    Estado: str
    IIBB: str
    Vendedor: int
    FormaPago: int
    ListaPrecio: int
    TipoDocumento: int
    Repartidor: int
    Cobrador: int
    Rubro: int
    Observacion: str
    VtoCUIT: datetime
    Abasto: int
    OrdenZona: int
    DiasToleranciaVto: int
    Clave: str
    TipoPeriodo: str
