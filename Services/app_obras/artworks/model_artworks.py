# Imports de terceros
from sqlalchemy import Column, Integer, String, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship

# Imports del proyecto
from ....db.database import Base

class Artworks(Base):
    __tablename__ = 'artworks'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    inventory_code = Column(String(50), unique=True, nullable=False, index=True)
    thumbnail_url = Column(String(500), nullable=True)
    artist_id = Column(Integer, ForeignKey('artists.id'), nullable=False)
    title = Column(String(255), nullable=False)
    nickname = Column(String(255), nullable=True)
    creation_year = Column(Integer, nullable=False)
    technique = Column(String(255), nullable=False)
    materials = Column(String(500), nullable=False)
    dimensions = Column(String(100), nullable=False)
    internal_notes = Column(Text, nullable=True)
    photo_credit = Column(String(255), nullable=True)
    state_id = Column(Integer, ForeignKey('artwork_states.id'), nullable=False)
    is_available = Column(Boolean, default=True)
    is_sold = Column(Boolean, default=False)
    is_secondary_market = Column(Boolean, default=False)
    technical_sheet_url = Column(String(500), nullable=True)
    
    # Relaciones
    artist = relationship("Artists", back_populates="artworks")
    state = relationship("ArtworkStates", back_populates="artworks")
    exhibitions = relationship("Exhibitions", back_populates="artwork")
    sales = relationship("Sales", back_populates="artwork")
    documents = relationship("Documents", back_populates="artwork")
