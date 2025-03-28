from sqlalchemy import Column, Integer, String, Boolean, Float, Date, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from db.database import Base

class Prueba3(Base):
    __tablename__ = 'prueba3'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    test1 = Column(String(255))
