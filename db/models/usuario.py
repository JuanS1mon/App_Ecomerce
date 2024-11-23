from sqlalchemy import Column, Integer, NVARCHAR, Boolean, Float
from ..database import Base


class usuario(Base):
    __tablename__ = 'usuario'

    id = Column(Integer, primary_key=True, index=True, default=0)
    username = Column(NVARCHAR(50), default=' ')
    email = Column(NVARCHAR(50), default=' ')
    password_hash = Column(NVARCHAR(50), default=' ')
    created_at = Column(NVARCHAR(50), default=' ')
    updated_at = Column(NVARCHAR(50), default=' ')
