# Imports de terceros
from sqlalchemy import Boolean, Column, Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

# Imports del proyecto
from sql_app.db.database import Base

class Depositos(Base):
    __tablename__ = 'depositos'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    descripcion = Column(String(255))
    codigo = Column(String(255))
    observacion = Column(String(255))
    
    # Relaciones (temporalmente comentadas hasta resolver la estructura de FK)
    # ots = relationship("OT", back_populates="deposito", foreign_keys="OT.id_deposito")
