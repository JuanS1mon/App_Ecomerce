from sqlalchemy import Column, Integer, String, Boolean, Float, Date, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from db.database import Base

class Test1(Base):
    __tablename__ = 'test1'

    id = Column(String(255), primary_key=True, index=True)
    test1 = Column(String(255))
