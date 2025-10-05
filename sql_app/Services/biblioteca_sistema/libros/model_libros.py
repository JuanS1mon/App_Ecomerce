# ============================================================================
# MODELO: LIBROS
# ============================================================================
"""
Modelo para libros
Parte del servicio: biblioteca_sistema
Catálogo de libros de la biblioteca
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sql_app.db.database import Base
from datetime import datetime

class Libros(Base):
    """
    Modelo para libros
    Catálogo de libros de la biblioteca
    """
    __tablename__ = "libros"
    
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    titulo = Column(String(200), nullable=False)
    isbn = Column(String(20), nullable=False, unique=True)
    autor_id = Column(Integer, ForeignKey("autores.id"), nullable=False)
    disponible = Column(Boolean, nullable=False)

    def __repr__(self):
        return f"<Libros(id={self.id})>"
