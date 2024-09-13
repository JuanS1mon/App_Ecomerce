from sqlalchemy import Column, Integer, NVARCHAR, Boolean, Float
from ..database import Base


class Productos(Base):
    __tablename__ = 'productos'

    id = Column(Integer, primary_key=True, index=True, default=0)
    nombre = Column(NVARCHAR(50), default=' ')
    descripcion = Column(NVARCHAR(50), default=' ')
    precio = Column(Float, default=0.0)
    stock_cantidad = Column(Float, default=0.0)
    Id_compania = Column(Integer, primary_key=True, index=True, default=0)
    created_at = Column(NVARCHAR(50), default=' ')
    updated_at = Column(NVARCHAR(50), default=' ')
