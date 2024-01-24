from sqlalchemy import Column, Integer, Float, String, DateTime
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Articulos(Base):
    __tablename__ = 'Articulos'
    Codigo = Column(Integer, primary_key=True)
    Descripcion = Column(String(50))
    DescripcionCorta = Column(String(50))
    IVA = Column(Integer, primary_key=True)
    Proveedor = Column(Integer, primary_key=True)
    Departamento = Column(Integer, primary_key=True)
    Marca = Column(Integer, primary_key=True)
    Familia = Column(Integer, primary_key=True)
    UxB = Column(Integer, primary_key=True)
    BalDiasVto = Column(Integer, primary_key=True)
    BalCodigo = Column(Integer, primary_key=True)
    Tipo = Column(String(50))
    FechaModificacion = Column(DateTime)
    FechaAlta = Column(DateTime)
    HoraModificacion = Column(String(50))
    Deposito = Column(Integer, primary_key=True)
    PresentacionUnidad = Column(String(50))
    Ruteo = Column(String(50))
    Alfa = Column(String(50))
    CxB = Column(Integer, primary_key=True)
    SubFamilia = Column(Integer, primary_key=True)
    DiasAlVto = Column(Integer, primary_key=True)
    ModeloEtiqueta = Column(String(50))
    CantidadEtiquetas = Column(Integer, primary_key=True)
    CxP = Column(Integer, primary_key=True)
    CxPP = Column(Integer, primary_key=True)
    Sector = Column(Integer, primary_key=True)

from pydantic import BaseModel

class ArticulosModel(BaseModel):
    Codigo: int
    Descripcion: str
    DescripcionCorta: str
    IVA: int
    Proveedor: int
    Departamento: int
    Marca: int
    Familia: int
    UxB: int
    BalDiasVto: int
    BalCodigo: int
    Tipo: str
    FechaModificacion: datetime
    FechaAlta: datetime
    HoraModificacion: str
    Deposito: int
    PresentacionUnidad: str
    Ruteo: str
    Alfa: str
    CxB: int
    SubFamilia: int
    DiasAlVto: int
    ModeloEtiqueta: str
    CantidadEtiquetas: int
    CxP: int
    CxPP: int
    Sector: int
