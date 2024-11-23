from sqlalchemy import Column, Integer, String, Boolean, Float
from ..database import Base


class users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True, default=0)
    name = Column(String, default=' ')
    email = Column(String, default=' ')
    hashed_passwrd = Column(String, default=' ')
