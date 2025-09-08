# Imports de terceros
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

# Imports del proyecto
from ....db.database import Base

class Artists(Base):
    __tablename__ = 'artists'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    full_name = Column(String(255), nullable=False, index=True)
    
    # Relaciones
    artworks = relationship("Artworks", back_populates="artist")
