from sqlalchemy import Column, Integer, Float, String, DateTime
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Agrupadosdetalle(Base):
    __tablename__ = 'AgrupadosDetalle'
    Grupo = Column(Integer, primary_key=True)
    Codigo = Column(Integer, primary_key=True)

from pydantic import BaseModel

class AgrupadosdetalleModel(BaseModel):
    Grupo: int
    Codigo: int
