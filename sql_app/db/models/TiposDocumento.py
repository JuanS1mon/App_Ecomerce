from sqlalchemy import Column, Integer, Float, String, DateTime
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Tiposdocumento(Base):
    __tablename__ = 'TiposDocumento'
    Codigo = Column(Integer, primary_key=True)
    Descripcion = Column(String(50))

from pydantic import BaseModel

class TiposdocumentoModel(BaseModel):
    Codigo: int
    Descripcion: str
