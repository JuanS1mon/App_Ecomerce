# ============================================================================
# MODELO: AUTORES
# ============================================================================
"""
Modelo para autores
Parte del servicio: biblioteca_sistema
Información de autores de libros
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sql_app.db.database import Base
from datetime import datetime

class Autores(Base):
    """
    Modelo para autores
    Información de autores de libros
    """
    __tablename__ = "autores"
    
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    nombre = Column(String(100), nullable=False)
    email = Column(String(150))
    fecha_nacimiento = Column(DateTime)

    def __repr__(self):
        return f"<Autores(id={self.id})>"
