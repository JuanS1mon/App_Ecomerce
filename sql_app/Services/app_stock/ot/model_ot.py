# Imports de bibliotecas estándar
import datetime

# Imports de terceros
from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship

# Imports del proyecto
from sql_app.db.database import Base

class OT(Base):
    """
    Modelo para las Órdenes de Trabajo (OT)
    """
    __tablename__ = "ot"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_trabajo = Column(String(50), index=True)
    titulo = Column(String(255))
    area = Column(String(100), nullable=True)
    personal = Column(String(100), nullable=True)
    tiempo_estimado = Column(String(50), nullable=True)
    descripcion = Column(Text, nullable=True)
    id_deposito = Column(Integer, ForeignKey("depositos.id"), nullable=True)
    estado = Column(String(20), default="pendiente")  # pendiente, en_proceso, finalizada, cancelada
    fecha_creacion = Column(DateTime, default=datetime.datetime.utcnow)
    fecha_inicio = Column(DateTime, nullable=True)
    fecha_fin = Column(DateTime, nullable=True)
    
    # Relaciones
    deposito = relationship("Depositos", foreign_keys=[id_deposito], back_populates="ots")
    operaciones = relationship("Operacion", back_populates="ot", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<OT(id={self.id}, id_trabajo='{self.id_trabajo}', estado='{self.estado}')>"


class Operacion(Base):
    """
    Modelo para las operaciones o tareas asociadas a una OT
    """
    __tablename__ = "ot_operaciones"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ot_id = Column(Integer, ForeignKey("ot.id", ondelete="CASCADE"), nullable=False)
    descripcion = Column(String(255), nullable=False)
    responsable = Column(String(100), nullable=True)
    tiempo_estimado = Column(Float, nullable=True)
    orden = Column(Integer, default=1)
    estado = Column(String(20), default="pendiente")  # pendiente, en_proceso, finalizada
    
    # Relaciones
    ot = relationship("OT", back_populates="operaciones")
    reportes_tiempo = relationship("ReporteTiempo", back_populates="operacion", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Operacion(id={self.id}, ot_id={self.ot_id}, descripcion='{self.descripcion}')>"


class ReporteTiempo(Base):
    """
    Modelo para los reportes de tiempo asociados a las operaciones
    """
    __tablename__ = "ot_reportes_tiempo"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    operacion_id = Column(Integer, ForeignKey("ot_operaciones.id", ondelete="CASCADE"), nullable=False)
    horas = Column(Float, nullable=False)
    usuario = Column(String(100), nullable=False)
    descripcion = Column(Text, nullable=True)
    fecha = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relaciones
    operacion = relationship("Operacion", back_populates="reportes_tiempo")
    
    def __repr__(self):
        return f"<ReporteTiempo(id={self.id}, operacion_id={self.operacion_id}, horas={self.horas})>"