from sqlalchemy import Column, Integer, String, Boolean, Float, Date, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from db.database import Base

class EcomerceCategorias(Base):
    __tablename__ = 'ecomerce_categorias'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(255))
    descripcion = Column(String(255))
    imagen_url = Column(String(500))
    id_padre = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())
    active = Column(Boolean, default=False)
