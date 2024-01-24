from sqlalchemy import Column, Integer, Float, String, DateTime
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Clases(Base):
    __tablename__ = 'Clases'
    Codigo = Column(Integer, primary_key=True)
    Descripcion = Column(String(50))

from pydantic import BaseModel

class ClasesModel(BaseModel):
    Codigo: int
    Descripcion: str
