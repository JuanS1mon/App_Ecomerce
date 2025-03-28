from sqlalchemy import Column, Integer, String, Boolean, Float
from ..database import Base

class Test(Base):
    __tablename__ = 'test'

    id = Column(Integer, primary_key=True, index=True, default=0)
    campo1 = Column(String(50), default=' ')
