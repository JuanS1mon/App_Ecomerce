# Imports de bibliotecas estándar
from datetime import datetime

# Imports de terceros
from sqlalchemy import Column, DateTime, Integer, NVARCHAR, Boolean,func

# Imports del proyecto
from ..database import Base

class BlogPost(Base):
    __tablename__ = "blog_posts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(NVARCHAR(50), default=' ')
    content = Column(NVARCHAR(250), default=' ')
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())