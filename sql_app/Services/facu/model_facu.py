from sqlalchemy import Column, Integer, String, Boolean, Float
from db.database import Base

class Facu(Base):
    __tablename__ = 'facu'
    __table_args__ = {'extend_existing': True}  # Añade esto para permitir redefinición

    id = Column(Integer, primary_key=True, index=True, default=0)
    asd = Column(String(50), default=' ')