from sqlalchemy import Column, Integer, String, Boolean, Float, Date, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from db.database import Base

class Facu_gay(Base):
    __tablename__ = 'facu_gay'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    codigo = Column(Integer, default=0)
    re = Column(String(255))
