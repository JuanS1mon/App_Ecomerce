# Imports de terceros
from sqlalchemy import Column, Integer, NVARCHAR, Boolean, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

# Imports del proyecto
from ...database import Base

# Tabla de asociación muchos-a-muchos para usuarios y roles
usuario_roles = Table(
    'usuario_roles',
    Base.metadata,
    Column('usuario_id', Integer, ForeignKey('Usuarios.codigo'), primary_key=True),
    Column('rol_id', Integer, ForeignKey('Roles.id'), primary_key=True)
)

class Roles(Base):
    __tablename__ = "Roles"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(NVARCHAR(50), unique=True, nullable=False)
    descripcion = Column(NVARCHAR(200), nullable=True)