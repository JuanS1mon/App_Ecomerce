"""
Sistema de Chat Global - Modelos de Base de Datos
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class ChatRoom(Base):
    """Salas de chat"""
    __tablename__ = "chat_rooms"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text)
    tipo = Column(String(20), default="publico")  # publico, privado, grupo
    activo = Column(Boolean, default=True)
    creado_por = Column(Integer, ForeignKey("usuarios.codigo"))
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    
    # Relaciones
    mensajes = relationship("ChatMessage", back_populates="sala")
    miembros = relationship("ChatMember", back_populates="sala")

class ChatMessage(Base):
    """Mensajes de chat"""
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    sala_id = Column(Integer, ForeignKey("chat_rooms.id"))
    usuario_id = Column(Integer, ForeignKey("usuarios.codigo"))
    contenido = Column(Text, nullable=False)
    tipo = Column(String(20), default="texto")  # texto, imagen, archivo, sistema
    fecha_envio = Column(DateTime, default=datetime.utcnow)
    editado = Column(Boolean, default=False)
    fecha_edicion = Column(DateTime)
    eliminado = Column(Boolean, default=False)
    
    # Relaciones
    sala = relationship("ChatRoom", back_populates="mensajes")
    leido_por = relationship("ChatReadStatus", back_populates="mensaje")

class ChatMember(Base):
    """Miembros de salas de chat"""
    __tablename__ = "chat_members"
    
    id = Column(Integer, primary_key=True, index=True)
    sala_id = Column(Integer, ForeignKey("chat_rooms.id"))
    usuario_id = Column(Integer, ForeignKey("usuarios.codigo"))
    rol = Column(String(20), default="miembro")  # admin, moderador, miembro
    fecha_union = Column(DateTime, default=datetime.utcnow)
    activo = Column(Boolean, default=True)
    
    # Relaciones
    sala = relationship("ChatRoom", back_populates="miembros")

class ChatReadStatus(Base):
    """Estado de lectura de mensajes"""
    __tablename__ = "chat_read_status"
    
    id = Column(Integer, primary_key=True, index=True)
    mensaje_id = Column(Integer, ForeignKey("chat_messages.id"))
    usuario_id = Column(Integer, ForeignKey("usuarios.codigo"))
    fecha_lectura = Column(DateTime, default=datetime.utcnow)
    
    # Relaciones
    mensaje = relationship("ChatMessage", back_populates="leido_por")
