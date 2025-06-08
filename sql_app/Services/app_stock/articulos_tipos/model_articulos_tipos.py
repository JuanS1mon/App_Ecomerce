# Imports de terceros
from sqlalchemy import Boolean, Column, Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.sql import func

# Imports del proyecto
from sql_app.db.database import Base

class Articulos_tipos(Base):
    __tablename__ = 'articulos_tipos'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    descripcion = Column(String(255))
