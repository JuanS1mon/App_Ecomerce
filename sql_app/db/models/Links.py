from sqlalchemy import Column, Integer, Float, String, DateTime
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Links(Base):
    __tablename__ = 'Links'
    CodigoArticulo = Column(Integer, primary_key=True)
    Tipo = Column(String(50))
    CantidadTipo = Column(String(50))
    FechaSincro = Column(DateTime)

from pydantic import BaseModel

class LinksModel(BaseModel):
    CodigoArticulo: int
    Tipo: str
    CantidadTipo: str
    FechaSincro: datetime
