from sqlalchemy import Column, Integer, Float, String, DateTime
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Articulosprecioslistas(Base):
    __tablename__ = 'ArticulosPreciosListas'
    Lista = Column(Integer, primary_key=True)
    Articulo = Column(Integer, primary_key=True)
    TipoValor = Column(String(50))
    FechaSincro = Column(DateTime)

from pydantic import BaseModel

class ArticulosprecioslistasModel(BaseModel):
    Lista: int
    Articulo: int
    TipoValor: str
    FechaSincro: datetime
