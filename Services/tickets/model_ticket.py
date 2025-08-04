"""

from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON, String, Text

from sqlalchemy.sql import func

from sql_app.db.database import Baseclass Ticket(Base):

    Modelo para la tabla de tickets en la base de datos.
    IMPORTANTE: Solo incluir columnas que existen en la tabla real.
    """
    __tablename__ = 'tickets'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    titulo = Column(String(255), nullable=False)
    descripcion = Column(Text, nullable=False)
    categoria = Column(String(100), nullable=False)
    prioridad = Column(String(50), nullable=False)  # baja, media, alta, critica
    estado = Column(String(50), nullable=False, default='abierto')  # abierto, proceso, cerrado
    
    # Información del solicitante
    solicitante = Column(String(255))
    email = Column(String(255))
    telefono = Column(String(50), default='')
    departamento = Column(String(100), default='')
    
    # Campos de auditoría
    fecha_creacion = Column(DateTime, default=func.now())
    ultima_actualizacion = Column(DateTime, onupdate=func.now())
    
    # Historial de cambios como JSON
    historial = Column(JSON, default=list)
    
    # Campos para gestión
    asignado_a = Column(String(255), default='')
    tiempo_estimado = Column(Integer, default=0)
    tiempo_real = Column(Integer, default=0)
    
    # Nueva columna que añadiste recientemente
    ultima_respuesta = Column(Text, nullable=True)
    
    # NOTA: Comentarios no existe en la tabla - comentado para evitar errores
    # comentarios = Column(JSON, default=list)
    
    # NOTA: fecha_cierre no existe en la tabla - comentado para evitar errores
    # fecha_cierre = Column(DateTime, nullable=True)