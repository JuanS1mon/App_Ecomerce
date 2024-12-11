from sqlalchemy import Column, Integer, String, Boolean, Float
from ..database import Base

class Dieta(Base):
    __tablename__ = 'dieta'

    id = Column(Integer, primary_key=True, index=True, default=0)
    comida = Column(String(50), default=' ')
    fecha = Column(String(50), default=' ')
    categoria = Column(String(50), default=' ')
    dia = Column(String(50), default=' ')
