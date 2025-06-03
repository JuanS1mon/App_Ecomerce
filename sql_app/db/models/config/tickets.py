"""
Modelo SQLAlchemy para el sistema de tickets
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from datetime import datetime

try:
    from ...database import Base
except ImportError:
    from sql_app.db.database import Base

class Ticket(Base):
    __tablename__ = 'tickets'

    # Campos principales
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    titulo = Column(String(255), nullable=False, index=True)
    descripcion = Column(Text, nullable=False)
    categoria = Column(String(100), nullable=False, index=True)
    prioridad = Column(String(50), nullable=False, default="media", index=True)  # baja, media, alta, critica
    estado = Column(String(50), nullable=False, default="abierto", index=True)  # abierto, proceso, cerrado
    
    # Información del solicitante
    solicitante = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    telefono = Column(String(50), nullable=True)
    departamento = Column(String(100), nullable=True)
    
    # Asignación y tiempos
    asignado_a = Column(String(255), nullable=True)
    tiempo_estimado = Column(Integer, nullable=True)  # en minutos
    tiempo_real = Column(Integer, nullable=True)      # en minutos
    
    # Fechas
    fecha_creacion = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    ultima_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Historial como JSON
    historial = Column(JSON, nullable=True)
    
    def __repr__(self):
        return f"<Ticket(id={self.id}, titulo='{self.titulo}', estado='{self.estado}')>"
