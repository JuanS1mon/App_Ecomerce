from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from db.database import Base

class Presupuesto(Base):
    __tablename__ = 'presupuestos'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    telefono = Column(String(50), nullable=False)
    mensaje = Column(Text, nullable=False)
    estado = Column(String(50), default='pendiente')  # pendiente, contactado, aprobado, rechazado
    fecha_creacion = Column(DateTime, default=func.now())
    fecha_actualizacion = Column(DateTime, default=func.now(), onupdate=func.now())