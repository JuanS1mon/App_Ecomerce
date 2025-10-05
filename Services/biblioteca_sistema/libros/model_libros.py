# ============================================================================
# MODELO: LIBROS
# ============================================================================
"""
Modelo para libros
Parte del servicio: biblioteca_sistema
Tabla de libros
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sql_app.db.database import Base
from datetime import datetime

class Libros(Base):
    """
    Modelo para libros
    Tabla de libros
    """
    __tablename__ = "libros"
    
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    titulo = Column(String(200), nullable=False)
    isbn = Column(String(20), unique=True)
    autor_id = Column(Integer, ForeignKey("autores.id"), nullable=False)
    fecha_publicacion = Column(DateTime)
    precio = Column(Numeric)

    def __repr__(self):
        return f"<Libros(id={self.id})>"
