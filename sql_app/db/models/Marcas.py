from sqlalchemy import Column, Integer, String, Boolean, Numeric
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Usuario(Base):
    __tablename__ = 'Usuarios'

    Codigo = Column(Integer, primary_key=True)
    Usuario = Column(String(50), nullable=False, default='')
    Clave = Column(String(20), nullable=False, default='')
    NombreCompleto = Column(String(50), nullable=False, default='')
    Sector = Column(String(50), nullable=False, default='')
    EMail = Column(String(255), nullable=False, default='')
    EstablecePermisos = Column(Boolean, nullable=False, default=False)
    Direccion = Column(String(100), nullable=False, default='')
    Telefono = Column(String(50), nullable=False, default='')
    Interno = Column(String(20), nullable=False, default='')
    DNI = Column(String(20), nullable=False, default='')
    Habilitado = Column(Boolean, nullable=False, default=True)
    Transmitido = Column(Boolean, nullable=False, default=False)
    EsVendedor = Column(Boolean, nullable=False, default=False)
    EsCobrador = Column(Boolean, nullable=False, default=False)
    EsRepartidor = Column(Boolean, nullable=False, default=False)
    EsCajero = Column(Boolean, nullable=False, default=False)
    PorcComisionCobranza = Column(Numeric, nullable=False, default=0)
    PorcComisionVenta = Column(Numeric, nullable=False, default=0)
    Nivel = Column(Integer, nullable=False, default=0)
    HabilControl = Column(Boolean, nullable=False, default=False)
    Legajo = Column(String(15), nullable=False, default='')
    Sucursal = Column(Integer, nullable=False, default=0)
    DuracionJornada = Column(Integer, nullable=False, default=0)