from sqlalchemy import Column, Integer, NVARCHAR, Boolean, Float
from ..database import Base


class inventarios(Base):
    __tablename__ = 'inventarios'

    id = Column(Integer, primary_key=True, index=True, default=0)
    producto_id = Column(Integer, primary_key=True, index=True, default=0)
    cantidad_fisica = Column(Float, default=0.0)
    inventario_date = Column(NVARCHAR(50), default=' ')
    notas = Column(NVARCHAR(50), default=' ')
    created_at = Column(NVARCHAR(50), default=' ')
    updated_at = Column(NVARCHAR(50), default=' ')
