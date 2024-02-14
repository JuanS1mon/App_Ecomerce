from sqlalchemy import Column, Integer, Float, String, DateTime
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Chequeras(Base):
    __tablename__ = 'Chequeras'
    Empresa = Column(Integer, primary_key=True)
    Numero = Column(Integer, primary_key=True)
    Banco = Column(Integer, primary_key=True)
    FechaChequera = Column(DateTime)

from pydantic import BaseModel

class ChequerasModel(BaseModel):
    Empresa: int
    Numero: int
    Banco: int
    FechaChequera: datetime
