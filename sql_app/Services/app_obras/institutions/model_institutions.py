# Imports de terceros
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

# Imports del proyecto
from ....db.database import Base

class Institutions(Base):
    __tablename__ = 'institutions'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    location_id = Column(Integer, ForeignKey('locations.id'), nullable=False)
    
    # Relaciones
    location = relationship("Locations", back_populates="institutions")
    exhibitions = relationship("Exhibitions", back_populates="institution")
