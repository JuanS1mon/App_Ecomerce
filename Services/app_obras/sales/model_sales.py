# Imports de terceros
from sqlalchemy import Column, Integer, String, Numeric, ForeignKey
from sqlalchemy.orm import relationship

# Imports del proyecto
from ....db.database import Base

class Sales(Base):
    __tablename__ = 'sales'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    artwork_id = Column(Integer, ForeignKey('artworks.id'), nullable=False)
    sale_year = Column(Integer, nullable=False)
    gallery = Column(String(255), nullable=False)
    buyer_collection = Column(String(255), nullable=False)
    buyer_mention = Column(String(255), nullable=True)
    location_id = Column(Integer, ForeignKey('locations.id'), nullable=False)
    intermediary = Column(String(255), nullable=True)
    provenance = Column(String(500), nullable=True)
    list_value = Column(Numeric(10, 2), nullable=False)
    real_value = Column(Numeric(10, 2), nullable=False)
    artist_share_percent = Column(Numeric(5, 2), nullable=False)
    payment_status = Column(String(50), nullable=False)  # Pagado / Parcial / No
    pending_amount = Column(Numeric(10, 2), nullable=False, default=0)
    
    # Relaciones
    artwork = relationship("Artworks", back_populates="sales")
    location = relationship("Locations", back_populates="sales")
