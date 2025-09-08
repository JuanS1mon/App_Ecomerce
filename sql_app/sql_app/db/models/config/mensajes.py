# Imports de terceros
from sqlalchemy import Column, Integer, NVARCHAR, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

# Imports del proyecto
from ...database import Base

class Mensajes(Base):
    __tablename__ = 'mensajes'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Usuario que envía el mensaje (puede ser None para mensajes del sistema)
    usuario_emisor_id = Column(Integer, ForeignKey('Usuarios.codigo'), nullable=True)
    
    # Usuario que recibe el mensaje
    usuario_receptor_id = Column(Integer, ForeignKey('Usuarios.codigo'), nullable=False)
    
    # Título del mensaje
    titulo = Column(NVARCHAR(200), nullable=False)
    
    # Contenido del mensaje
    contenido = Column(Text, nullable=False)
    
    # Tipo de mensaje (sistema, usuario, alerta, etc.)
    tipo = Column(NVARCHAR(50), default='usuario')
    
    # Prioridad del mensaje (baja, normal, alta, urgente)
    prioridad = Column(NVARCHAR(20), default='normal')
    
    # Estado de lectura
    leido = Column(Boolean(create_constraint=False), default=False)
    
    # Fechas
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    fecha_lectura = Column(DateTime(timezone=True), nullable=True)
    
    # Metadatos adicionales (JSON string para flexibilidad)
    metadatos = Column(Text, nullable=True)
    
    # Si el mensaje está activo (para soft delete)
    activo = Column(Boolean(create_constraint=False), default=True)
