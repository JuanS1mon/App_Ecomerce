from sqlalchemy import Column, Integer, String, Boolean, Float, Date, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from db.database import Base

class Prueba2(Base):
    __tablename__ = 'prueba2'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    coa = Column(String(255))
