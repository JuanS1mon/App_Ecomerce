from sqlalchemy import Column, Integer, Float, String, DateTime
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Formaspagos(Base):
    __tablename__ = 'FormasPagos'
    Codigo = Column(Integer, primary_key=True)
    Descripcion = Column(String(50))
    Dias = Column(Integer, primary_key=True)

from pydantic import BaseModel

class FormaspagosModel(BaseModel):
    Codigo: int
    Descripcion: str
    Dias: int
