from sqlalchemy import Column, Integer, String, Boolean, Float
from ..database import Base

class Carga(Base):
    __tablename__ = 'carga'

    nrosuceso = Column(Integer, primary_key=True, index=True, default=0)
    fecha = Column(String(50), default=' ')
    origen = Column(String(50), default=' ')
    tipo = Column(String(50), default=' ')
    caratula = Column(String(50), default=' ')
    clasificacion = Column(String(50), default=' ')
    estado = Column(String(50), default=' ')
