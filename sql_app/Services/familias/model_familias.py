from sqlalchemy import Column, Integer, String, Boolean, Float
from ..database import Base

class Familias(Base):
    __tablename__ = 'familias'

    tetwe = Column(Integer, primary_key=True, index=True, default=0)
    asd = Column(String(50), default=' ')
