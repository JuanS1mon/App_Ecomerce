# Imports de terceros
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

# Imports del proyecto
from ....db.database import Base

class ArtworkStates(Base):
    __tablename__ = 'artwork_states'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    description = Column(String(255), nullable=False)
    
    # Relaciones
    artworks = relationship("Artworks", back_populates="state")
