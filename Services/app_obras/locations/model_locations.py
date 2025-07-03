# Imports de terceros
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

# Imports del proyecto
from ....db.database import Base

class Locations(Base):
    __tablename__ = 'locations'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    city = Column(String(255), nullable=False)
    country = Column(String(255), nullable=False)
    address = Column(String(500), nullable=True)
    
    # Relaciones
    institutions = relationship("Institutions", back_populates="location")
    sales = relationship("Sales", back_populates="location")
