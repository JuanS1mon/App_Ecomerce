from sqlalchemy import Column, Integer, Float, String, DateTime
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Empresas(Base):
    __tablename__ = 'Empresas'
    Numero = Column(Integer, primary_key=True)
    Nombre = Column(String(50))
    CUIT = Column(String(50))
    EjercicioActual = Column(Integer, primary_key=True)
    FechaCierreCaja = Column(DateTime)
    Logo = Column(String(50))
    RazonSocial = Column(String(50))
    Direccion = Column(String(50))
    NroAgRet = Column(String(50))
    OrdenPago = Column(Integer, primary_key=True)
    R_IIBB = Column(Integer, primary_key=True)
    R_gan = Column(Integer, primary_key=True)
    OPCant = Column(Integer, primary_key=True)
    RetCant = Column(Integer, primary_key=True)
    FechaCierreIva = Column(DateTime)
    FechaProximoCierreIva = Column(DateTime)
    TipoOrdenPago = Column(Integer, primary_key=True)
    Color = Column(Integer, primary_key=True)
    FormatoRecibo = Column(Integer, primary_key=True)
    FechaCierreBancos = Column(DateTime)
    PathOP = Column(String(50))
    PathRET = Column(String(50))
    Localidad = Column(Integer, primary_key=True)
    PathLogoOP = Column(String(50))
    AFIP_URLTFA = Column(String(50))
    AFIP_URLPFX = Column(String(50))
    PuntoVentaComision = Column(Integer, primary_key=True)
    PuertoImpresionDP = Column(String(50))
    NroAgRetAGIP = Column(String(50))
    NroAgRetIIBB = Column(String(50))
    NroAgRetAPR = Column(String(50))
    BancoDefecto = Column(Integer, primary_key=True)

from pydantic import BaseModel

class EmpresasModel(BaseModel):
    Numero: int
    Nombre: str
    CUIT: str
    EjercicioActual: int
    FechaCierreCaja: datetime
    Logo: str
    RazonSocial: str
    Direccion: str
    NroAgRet: str
    OrdenPago: int
    R_IIBB: int
    R_gan: int
    OPCant: int
    RetCant: int
    FechaCierreIva: datetime
    FechaProximoCierreIva: datetime
    TipoOrdenPago: int
    Color: int
    FormatoRecibo: int
    FechaCierreBancos: datetime
    PathOP: str
    PathRET: str
    Localidad: int
    PathLogoOP: str
    AFIP_URLTFA: str
    AFIP_URLPFX: str
    PuntoVentaComision: int
    PuertoImpresionDP: str
    NroAgRetAGIP: str
    NroAgRetIIBB: str
    NroAgRetAPR: str
    BancoDefecto: int
