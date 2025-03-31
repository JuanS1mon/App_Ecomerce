from sqlalchemy import Column, Integer, NVARCHAR, Table
from db.database import Base

class roles(Base):
    __tablename__ = "Roles"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(NVARCHAR(50), unique=True, nullable=False)
    descripcion = Column(NVARCHAR(200), nullable=True)