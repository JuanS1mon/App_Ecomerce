from sqlalchemy import Column, Integer, Float, String, DateTime
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Proveedores(Base):
    __tablename__ = 'Proveedores'
    Codigo = Column(Integer, primary_key=True)
    Nombre = Column(String(50))
    RazonSocial = Column(String(50))
    CUIT = Column(String(50))
    Direccion = Column(String(50))
    Localidad = Column(Integer, primary_key=True)
    Telefono = Column(String(50))
    Telefono2 = Column(String(50))
    Fax = Column(String(50))
    Contacto = Column(String(50))
    RetieneGanancias = Column(Integer, primary_key=True)
    NroIIBB = Column(String(50))
    Email = Column(String(50))
    PaginaWeb = Column(String(50))
    ReferenciaProv = Column(String(50))
    TipoIVA = Column(String(50))
    Celular = Column(String(50))
    Rubro = Column(String(50))
    HorarioAtencion = Column(String(50))
    FormaPago = Column(Integer, primary_key=True)
    CodigoPostal = Column(String(50))
    ContactoDireccion = Column(String(50))
    ContactoTelefono = Column(String(50))
    ContactoEmail = Column(String(50))
    FechaAlta = Column(DateTime)
    Observacion = Column(String(50))
    FormatoRecepcion = Column(Integer, primary_key=True)
    DiasBloqueoPagoPreDP = Column(Integer, primary_key=True)

from pydantic import BaseModel

class ProveedoresModel(BaseModel):
    Codigo: int
    Nombre: str
    RazonSocial: str
    CUIT: str
    Direccion: str
    Localidad: int
    Telefono: str
    Telefono2: str
    Fax: str
    Contacto: str
    RetieneGanancias: int
    NroIIBB: str
    Email: str
    PaginaWeb: str
    ReferenciaProv: str
    TipoIVA: str
    Celular: str
    Rubro: str
    HorarioAtencion: str
    FormaPago: int
    CodigoPostal: str
    ContactoDireccion: str
    ContactoTelefono: str
    ContactoEmail: str
    FechaAlta: datetime
    Observacion: str
    FormatoRecepcion: int
    DiasBloqueoPagoPreDP: int
