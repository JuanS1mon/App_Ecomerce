from sqlalchemy import Column, Integer, Float, String, DateTime
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Tiposcbtes(Base):
    __tablename__ = 'TiposCbtes'
    Codigo = Column(String(50))
    Descripcion = Column(String(50))
    Signo = Column(String(50))

from pydantic import BaseModel

class TiposcbtesModel(BaseModel):
    Codigo: str
    Descripcion: str
    Signo: str
