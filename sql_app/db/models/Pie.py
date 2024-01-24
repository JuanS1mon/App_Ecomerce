from sqlalchemy import Column, Integer, Float, String, DateTime
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Pie(Base):
    __tablename__ = 'Pie'
    Linea = Column(Integer, primary_key=True)
    Texto = Column(String(50))
    Sucursal = Column(Integer, primary_key=True)

from pydantic import BaseModel

class PieModel(BaseModel):
    Linea: int
    Texto: str
    Sucursal: int
