from sqlalchemy import Column, Integer, Float, String, DateTime
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Teclados(Base):
    __tablename__ = 'Teclados'
    Teclado = Column(Integer, primary_key=True)
    Descripcion = Column(String(50))

from pydantic import BaseModel

class TecladosModel(BaseModel):
    Teclado: int
    Descripcion: str
