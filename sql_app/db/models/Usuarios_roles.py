from sqlalchemy import Column, Integer, NVARCHAR, Boolean, Float
from ..database import Base


class Usuarios_roles(Base):
    __tablename__ = 'usuarios_roles'

    id = Column(Integer, primary_key=True, index=True, default=0)
    usuario_id = Column(Integer, primary_key=True, index=True, default=0)
    empresa_id = Column(Integer, primary_key=True, index=True, default=0)
    rol = Column(NVARCHAR(50), default=' ')
    created_at = Column(NVARCHAR(50), default=' ')
    updated_at = Column(NVARCHAR(50), default=' ')
