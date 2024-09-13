from sqlalchemy import Column, Integer, NVARCHAR, Boolean
from ..database import Base


class usuarios(Base):
    __tablename__ = 'usuarios'

    codigo = Column(Integer, primary_key=True, index=True, autoincrement=False)
    usuario = Column(NVARCHAR(50), unique=True, nullable=False)
    nombre = Column(NVARCHAR(100), nullable=False)
    mail = Column(NVARCHAR(100), unique=True, nullable=False)
    activo = Column(Boolean(create_constraint=False), default=True)
    clave = Column(NVARCHAR(250), nullable=False)