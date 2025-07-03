# Imports de terceros
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

# Imports del proyecto
from ....db.database import Base

class Documents(Base):
    __tablename__ = 'documents'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    artwork_id = Column(Integer, ForeignKey('artworks.id'), nullable=False)
    doc_type = Column(String(100), nullable=False)
    url = Column(String(500), nullable=False)
    
    # Relaciones
    artwork = relationship("Artworks", back_populates="documents")
