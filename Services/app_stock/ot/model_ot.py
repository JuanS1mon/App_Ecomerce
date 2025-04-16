from sqlalchemy import Column, Integer, String, Boolean, Float, Date, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from db.database import Base

class Ot(Base):
    __tablename__ = 'ot'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_trabajo = Column(String(255))
    area = Column(String(255))
    personal = Column(String(255))
    tiempo_estimado = Column(String(255))
