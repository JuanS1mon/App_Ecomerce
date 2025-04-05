from sqlalchemy import Column, Integer, String
from db.database import Base

class Roles(Base):
    __tablename__ = "Roles"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), unique=True)
    descripcion = Column(String(255), nullable=True)
