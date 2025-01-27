from sqlalchemy import Column, Integer, String, Boolean, Float
from ..database import Base

class Test4(Base):
    __tablename__ = 'test4'

    codigo = Column(Integer, primary_key=True, index=True, default=0)
    nombre = Column(String(50), default=' ')
    numero = Column(Integer, primary_key=True, index=True, default=0)
    veri = Column(Boolean, default=False)
