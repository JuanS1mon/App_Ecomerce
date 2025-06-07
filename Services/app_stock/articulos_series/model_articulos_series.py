from sqlalchemy import Column, Integer, String, Boolean, Float, Date, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from ....db.database import Base

class Articulos_series(Base):
    __tablename__ = 'articulos_series'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    serie = Column(String(255))
