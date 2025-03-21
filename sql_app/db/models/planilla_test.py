from sqlalchemy import Column, Integer, String
from ..database import Base

class Planilla_test(Base):
    __tablename__ = 'planilla_test'

    codigo = Column(Integer, primary_key=True, index=True)
    fecha = Column(String(50), nullable=True, default=None)
    origen = Column(String(50), nullable=True, default=None)
    tipo = Column(String(50), nullable=True, default=None)
    prioridad = Column(String(50), nullable=True, default=None)
    caratula = Column(String(50), nullable=True, default=None)
    clasificacion = Column(String(50), nullable=True, default=None)
    estado = Column(String(50), nullable=True, default=None)
    localidad = Column(String(50), nullable=True, default=None)
    barrio = Column(String(50), nullable=True, default=None)
    lugar = Column(String(50), nullable=True, default=None)
