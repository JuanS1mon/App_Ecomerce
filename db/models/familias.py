from sqlalchemy import Column, Integer, String, Boolean, Float
from ..database import Base

class Familias(Base):
    __tablename__ = 'familias'

    codigo = Column(Integer, primary_key=True, index=True, default=0)
    descrip = Column(String(50), default=' ')
