from sqlalchemy import Column, Integer, String, Boolean, Float
from ...db.database import Base

class Rubros(Base):
    __tablename__ = 'rubros'

    codigo = Column(Integer, primary_key=True, index=True, default=0)
    test1 = Column(String(50), default=' ')
    test2 = Column(Float, default=0.0)
    test3 = Column(Boolean, default=False)
