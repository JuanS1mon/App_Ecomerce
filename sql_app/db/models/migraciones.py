# db/models.py

from sqlalchemy import Column, Integer, String, Float,Boolean
from db.database import Base

class ModeloA(Base):
    __tablename__ = 'tabla_a'

    id = Column(Integer, primary_key=True, index=True)
    campo1 = Column(String)
    campo2 = Column(Integer)
    campo3 = Column(String)

class ModeloB(Base):
    __tablename__ = 'tabla_b'

    id = Column(Integer, primary_key=True, index=True)
    campo1 = Column(String)
    campo2 = Column(Integer)
    campo3 = Column(String)