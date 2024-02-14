from sqlalchemy import Column, Integer, Float, String, DateTime
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Plancuentas(Base):
    __tablename__ = 'PlanCuentas'
    Descripcion = Column(String(50))
    Empresa = Column(Integer, primary_key=True)
    TipoCuenta = Column(String(50))

from pydantic import BaseModel

class PlancuentasModel(BaseModel):
    Descripcion: str
    Empresa: int
    TipoCuenta: str
