from sqlalchemy import Column, Integer, NVARCHAR, Boolean, Float
from ..database import Base


class pruebe(Base):
    __tablename__ = 'pruebe'

    campoq = Column(Integer, primary_key=True, index=True, default=0)
    campob = Column(NVARCHAR(50), default=' ')
    campoc = Column(Float, default=0.0)
