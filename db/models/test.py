from sqlalchemy import Column, Integer, String, Boolean, Float
from ..database import Base

class Test(Base):
    __tablename__ = 'test'

    codigo = Column(Integer, primary_key=True, index=True, default=0)
    nombre = Column(String(50), default=' ')
