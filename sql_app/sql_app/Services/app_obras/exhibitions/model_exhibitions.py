# Imports de terceros
from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship

# Imports del proyecto
from ....db.database import Base

class Exhibitions(Base):
    __tablename__ = 'exhibitions'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    artwork_id = Column(Integer, ForeignKey('artworks.id'), nullable=False)
    name = Column(String(255), nullable=False)
    institution_id = Column(Integer, ForeignKey('institutions.id'), nullable=False)
    curator = Column(String(255), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    documentation_url = Column(String(500), nullable=False)
    
    # Relaciones con lazy loading para evitar problemas de importación circular
    artwork = relationship("Artworks", back_populates="exhibitions", lazy="select")
    institution = relationship("Institutions", back_populates="exhibitions", lazy="select")
    movements = relationship("Movements", back_populates="exhibition")
