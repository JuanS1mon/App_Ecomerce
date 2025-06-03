from sqlalchemy import Column, Integer, String, Boolean, Float, Date, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from db.database import Base

class Depositos(Base):
    __tablename__ = 'depositos'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    descripcion = Column(String(255))
    codigo = Column(String(255))
    observacion = Column(String(255))
    
    # Relaciones
    ots = relationship("OT", back_populates="deposito", foreign_keys="OT.id_deposito")
