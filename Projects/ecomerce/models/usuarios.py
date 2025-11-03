from sqlalchemy import Column, Integer, String, Boolean, Float, Date, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from db.database import Base

class EcomerceUsuarios(Base):
    __tablename__ = 'ecomerce_usuarios'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(255))
    apellido = Column(String(255))
    email = Column(String(255))
    contraseña_hash = Column(String(255))
    telefono = Column(String(255))
    direccion = Column(String(255))
    google_maps_link = Column(String(500))
    ciudad = Column(String(255))
    provincia = Column(String(255))
    pais = Column(String(255))
    created_at = Column(DateTime, default=func.now())
    active = Column(Boolean, default=False)
