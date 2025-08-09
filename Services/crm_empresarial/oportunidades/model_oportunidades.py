# ============================================================================
# MODELO: OPORTUNIDADES
# ============================================================================
"""
Modelo para oportunidades
Parte del servicio: crm_empresarial
Posibles ventas o proyectos
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sql_app.db.database import Base
from datetime import datetime

class Oportunidades(Base):
    """
    Modelo para oportunidades
    Posibles ventas o proyectos
    """
    __tablename__ = "oportunidades"
    
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    id_cliente = Column(Integer, nullable=False)
    titulo = Column(String(255), nullable=False)
    monto_estimado = Column(Integer, nullable=False)
    estado = Column(String(255), nullable=False)
    fecha_cierre = Column(DateTime)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    active = Column(Boolean, nullable=False)

    def __repr__(self):
        return f"<Oportunidades(id={self.id})">
