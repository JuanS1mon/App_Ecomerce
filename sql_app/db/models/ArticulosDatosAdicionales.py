from sqlalchemy import Column, Integer, Float, String, DateTime
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Articulosdatosadicionales(Base):
    __tablename__ = 'ArticulosDatosAdicionales'
    Campo = Column(String(50))
    Dato = Column(String(50))
    Articulo = Column(Integer, primary_key=True)
    FechaSincro = Column(DateTime)

from pydantic import BaseModel

class ArticulosdatosadicionalesModel(BaseModel):
    Campo: str
    Dato: str
    Articulo: int
    FechaSincro: datetime
