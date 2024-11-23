from sqlalchemy import Column, Integer, NVARCHAR, Boolean, Float
from ..database import Base


class test2(Base):
    __tablename__ = 'test2'

    campo1 = Column(Integer, primary_key=True, index=True, default=0)
    campo2 = Column(NVARCHAR(50), default=' ')
    campo3 = Column(Float, default=0.0)
