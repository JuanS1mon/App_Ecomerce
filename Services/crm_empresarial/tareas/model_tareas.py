# ============================================================================
# MODELO: TAREAS
# ============================================================================
"""
Modelo para tareas
Parte del servicio: crm_empresarial
Actividades o recordatorios
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sql_app.db.database import Base
from datetime import datetime

class Tareas(Base):
    """
    Modelo para tareas
    Actividades o recordatorios
    """
    __tablename__ = "tareas"
    
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    id_oportunidad = Column(Integer, nullable=False)
    descripcion = Column(String(255), nullable=False)
    fecha_vencimiento = Column(DateTime)
    completada = Column(Boolean, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    active = Column(Boolean, nullable=False)

    def __repr__(self):
        return f"<Tareas(id={self.id})">
