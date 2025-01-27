from sqlalchemy import Column, Integer, String, Boolean, Float
from ..database import Base

class Test3(Base):
    __tablename__ = 'test3'

    codigo = Column(Integer, primary_key=True, index=True, default=0)
    fecha = Column(String(50), default=' ')
    nombre = Column(String(50), default=' ')
