from sqlalchemy import Column, Integer, Float, String, DateTime
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Cuentasproveedores(Base):
    __tablename__ = 'CuentasProveedores'
    Proveedor = Column(Integer, primary_key=True)
    Banco = Column(String(50))
    SucursalBanco = Column(String(50))
    CuentaBancaria = Column(String(50))
    Moneda = Column(String(50))

from pydantic import BaseModel

class CuentasproveedoresModel(BaseModel):
    Proveedor: int
    Banco: str
    SucursalBanco: str
    CuentaBancaria: str
    Moneda: str
