from sqlalchemy import Column, Integer, String, Boolean, Float
from ..database import Base

class Pruebat1(Base):
    __tablename__ = 'pruebat1'

    campot1 = Column(Integer, primary_key=True, index=True, default=0)
    campot2 = Column(String(50), default=' ')
    campot3 = Column(Float, default=0.0)
    campot4 = Column(Boolean, default=False)