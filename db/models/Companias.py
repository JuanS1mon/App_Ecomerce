from sqlalchemy import Column, Integer, NVARCHAR, Boolean, Float
from ..database import Base


class Companias(Base):
    __tablename__ = 'companias'

    id = Column(Integer, primary_key=True, index=True, default=0)
    nombre = Column(NVARCHAR(50), default=' ')
    direccion = Column(NVARCHAR(50), default=' ')
    telefono = Column(NVARCHAR(50), default=' ')
    created_at = Column(NVARCHAR(50), default=' ')
    updated_at = Column(NVARCHAR(50), default=' ')
