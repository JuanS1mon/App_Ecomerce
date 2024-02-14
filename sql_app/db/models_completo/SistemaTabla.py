from sqlalchemy import Column, Integer, Float, String, DateTime
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Sistematabla(Base):
    __tablename__ = 'SistemaTabla'
    Campo = Column(String(50))
    Valor = Column(String(50))

from pydantic import BaseModel

class SistematablaModel(BaseModel):
    Campo: str
    Valor: str
