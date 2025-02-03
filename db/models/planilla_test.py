from sqlalchemy import Column, Integer, String, Boolean, Float
from ..database import Base

class Planilla_test(Base):
    __tablename__ = 'planilla_test'

    codigo = Column(Integer, primary_key=True, index=True, default=0)
    fecha = Column(String(50), default=' ')
    origen = Column(String(50), default=' ')
    tipo = Column(String(50), default=' ')
    prioridad = Column(String(50), default=' ')
    caratula = Column(String(50), default=' ')
    clasificacion = Column(String(50), default=' ')
    estado = Column(String(50), default=' ')
    localidad = Column(String(50), default=' ')
    barrio = Column(String(50), default=' ')
    lugar = Column(String(50), default=' ')
