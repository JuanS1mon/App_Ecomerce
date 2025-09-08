# Imports de terceros
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

# Imports del proyecto
from ....db.database import Base

class Contacts(Base):
    __tablename__ = 'contacts'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True, index=True)
    phone = Column(String(50), nullable=True)
    organization = Column(String(255), nullable=True)
    position = Column(String(255), nullable=True)
    address = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Un contacto puede estar relacionado con múltiples movimientos
    # pero no hacemos la relación directa aquí para mantener flexibilidad
