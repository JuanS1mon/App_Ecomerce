from sqlalchemy import Column, Integer, String, Boolean, Float, Date, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from db.database import Base

class Depositos_tipo(Base):
    __tablename__ = 'depositos_tipo'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    descripcion = Column(String(255))
