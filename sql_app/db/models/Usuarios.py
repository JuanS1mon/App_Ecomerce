from sqlalchemy import Column, Integer, Float, String, DateTime
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Usuarios(Base):
    __tablename__ = 'Usuarios'
    Codigo = Column(Integer, primary_key=True)
    Usuario = Column(String(50))
    Clave = Column(String(50))
    NombreCompleto = Column(String(50))
    Sector = Column(String(50))
    EMail = Column(String(50))
    Direccion = Column(String(50))
    Telefono = Column(String(50))
    Interno = Column(String(50))
    DNI = Column(String(50))
    Nivel = Column(Integer, primary_key=True)
    Legajo = Column(String(50))
    Sucursal = Column(Integer, primary_key=True)
    DuracionJornada = Column(Integer, primary_key=True)

from pydantic import BaseModel

class UsuariosModel(BaseModel):
    Codigo: int
    Usuario: str
    Clave: str
    NombreCompleto: str
    Sector: str
    EMail: str
    Direccion: str
    Telefono: str
    Interno: str
    DNI: str
    Nivel: int
    Legajo: str
    Sucursal: int
    DuracionJornada: int
