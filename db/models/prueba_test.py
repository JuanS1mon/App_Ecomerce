from sqlalchemy import Column, Integer, String, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class PruebaTest(Base):
    __tablename__ = 'prueba_test'

    campo1 = Column(Integer, primary_key=True, index=True, default=0)
    campostr = Column(String(50), default=' ')
    campofloat = Column(Float, default=0.0)