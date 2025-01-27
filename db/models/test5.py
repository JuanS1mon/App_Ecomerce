from sqlalchemy import Column, Integer, String, Boolean, Float
from ..database import Base

class Test5(Base):
    __tablename__ = 'test5'

    codigo = Column(Integer, primary_key=True, index=True, default=0)
    nombre = Column(String(50), default=' ')
    fecha = Column(String(50), default=' ')
    numerito = Column(Float, default=0.0)
    verif = Column(Boolean, default=False)
