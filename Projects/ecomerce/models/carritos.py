from sqlalchemy import Column, Integer, String, Boolean, Float, Date, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from db.database import Base

class EcomerceCarritos(Base):
    __tablename__ = 'ecomerce_carritos'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_usuario = Column(Integer, default=0)
    estado = Column(String(255))
    created_at = Column(DateTime, default=func.now())
