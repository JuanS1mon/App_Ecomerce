# Imports de terceros
from sqlalchemy import Column, Integer, NVARCHAR, Table

# Imports del proyecto
from ...database import Baseclass roles(Base):

    __tablename__ = "Roles"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(NVARCHAR(50), unique=True, nullable=False)
    descripcion = Column(NVARCHAR(200), nullable=True)