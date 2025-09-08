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
    numero = Column(String(50), index=True, nullable=False)  # Número de la OT
    fecha = Column(DateTime, nullable=False)  # Fecha de la OT
    cliente = Column(String(255), nullable=False)  # Cliente
    tipo = Column(String(50), nullable=True)  # Tipo de trabajo
    tecnico = Column(String(100), nullable=True)  # Técnico asignado
    descripcion = Column(Text, nullable=False)  # Descripción del trabajo
    id_deposito = Column(Integer, nullable=True)  # ForeignKey("depositos.id") comentado temporalmente
    estado = Column(String(20), default="planificando")  # planificando, ejecutando, finalizada
    fecha_creacion = Column(DateTime, default=datetime.datetime.utcnow)
    fecha_inicio = Column(DateTime, nullable=True)
    fecha_fin = Column(DateTime, nullable=True)
    
    # Campos heredados del modelo anterior (para compatibilidad)
    id_trabajo = Column(String(50), index=True, nullable=True)  # Deprecated
    titulo = Column(String(255), nullable=True)  # Deprecated
    area = Column(String(100), nullable=True)  # Deprecated
    personal = Column(String(100), nullable=True)  # Deprecated
    tiempo_estimado = Column(String(50), nullable=True)  # Deprecated
    
    # Relaciones
    # deposito = relationship("Depositos", foreign_keys=[id_deposito], back_populates="ots")
    operaciones = relationship("Operacion", back_populates="ot", cascade="all, delete-orphan")
    materiales = relationship("OTMaterial", back_populates="ot", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<OT(id={self.id}, numero='{self.numero}', cliente='{self.cliente}', estado='{self.estado}')>"


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
    estado = Column(String(20), default="planificando")  # planificando, ejecutando, finalizada
    
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


class OTMaterial(Base):
    """
    Modelo para los materiales asociados a las Órdenes de Trabajo
    Gestiona tanto los materiales planificados como los realmente utilizados
    """
    __tablename__ = "ot_materiales"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ot_id = Column(Integer, ForeignKey("ot.id", ondelete="CASCADE"), nullable=False)
    codigo_art = Column(Integer, nullable=False)  # Código del artículo
    id_deposito = Column(Integer, ForeignKey("depositos.id"), nullable=False)  # Depósito origen
    cantidad_planificada = Column(Float, default=0.0)  # Cantidad que se planifica usar
    cantidad_utilizada = Column(Float, default=0.0)    # Cantidad realmente utilizada
    cantidad_devuelta = Column(Float, default=0.0)     # Cantidad devuelta al stock
    estado = Column(String(20), default="planificado") # planificado, parcial, consumido, devuelto, cancelado
    fecha_planificacion = Column(DateTime, default=datetime.datetime.utcnow)
    fecha_consumo = Column(DateTime, nullable=True)
    fecha_devolucion = Column(DateTime, nullable=True)
    observacion = Column(Text, nullable=True)
    usuario_consumo = Column(String(100), nullable=True)  # Usuario que registró el consumo
    nro_movimiento_stock = Column(Integer, nullable=True)  # Número de movimiento de stock asociado
    
    # Relaciones
    ot = relationship("OT", foreign_keys=[ot_id])
    # deposito = relationship("Depositos", foreign_keys=[id_deposito])  # Comentado temporalmente
    
    def __repr__(self):
        return f"<OTMaterial(id={self.id}, ot_id={self.ot_id}, codigo_art={self.codigo_art}, estado='{self.estado}')>"
    
    @property
    def cantidad_pendiente(self):
        """Calcula la cantidad pendiente de utilizar"""
        return self.cantidad_planificada - self.cantidad_utilizada - self.cantidad_devuelta
    
    @property
    def porcentaje_utilizado(self):
        """Calcula el porcentaje de material utilizado respecto a lo planificado"""
        if self.cantidad_planificada > 0:
            return (self.cantidad_utilizada / self.cantidad_planificada) * 100
        return 0.0