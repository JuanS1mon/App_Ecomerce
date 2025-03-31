from sqlalchemy import Column, Integer, String, Boolean, Float, Date, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from db.database import Base

class Empleados(Base):
    __tablename__ = 'empleados'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    legajo = Column(String(255))
    nombre = Column(String(255))
    sector = Column(String(255))
    telefono = Column(String(255))
    email = Column(String(255))
    activo = Column(Boolean, default=False)
