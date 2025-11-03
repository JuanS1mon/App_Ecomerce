"""
Modelos de Base de Datos para el Sistema de Migraciones
========================================================

Este módulo contiene todos los modelos SQLAlchemy para el sistema de migraciones,
incluyendo metadata de migraciones, archivos cargados, conexiones externas,
logs de auditoría y mapeo de campos.

Autor: Sistema SQL App
Fecha: 18 de octubre de 2025
"""

from sqlalchemy import (
    Column, Integer, String, Text, DateTime, BigInteger, 
    Float, Boolean, ForeignKey, LargeBinary, JSON
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.database import Base
import json
from datetime import datetime
from typing import Dict, Any, Optional


class MigracionMetadata(Base):
    """
    Almacena información general sobre cada migración realizada.
    
    Esta tabla es el registro principal de todas las migraciones,
    ya sean desde archivos o desde bases de datos externas.
    """
    __tablename__ = "migraciones_metadata"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre_tabla = Column(String(255), nullable=False, index=True, 
                          comment="Nombre de la tabla creada en la BD")
    nombre_original_archivo = Column(String(500), 
                                    comment="Nombre original del archivo subido")
    tipo_archivo = Column(String(50), 
                         comment="Tipo: 'excel', 'csv', 'txt', 'sap', 'db_externa'")
    tamanio_bytes = Column(BigInteger, comment="Tamaño del archivo en bytes")
    total_registros = Column(Integer, default=0, 
                            comment="Total de registros migrados")
    estado = Column(String(50), default='procesando', index=True,
                   comment="Estado: 'procesando', 'completado', 'error', 'eliminado'")
    usuario_id = Column(Integer, nullable=True,
                       comment="Usuario que realizó la migración")
    fecha_creacion = Column(DateTime, default=func.now(), index=True,
                          comment="Fecha y hora de creación")
    fecha_actualizacion = Column(DateTime, onupdate=func.now(),
                                comment="Fecha de última actualización")
    mensaje_error = Column(Text, comment="Mensaje de error si falla")
    tiempo_procesamiento_segundos = Column(Float, 
                                          comment="Tiempo que tomó procesar")
    
    # Campos para validación de esquema post-creación
    validacion_errores = Column(JSON, comment="JSON con lista de errores de validación")
    validacion_advertencias = Column(JSON, comment="JSON con lista de advertencias de validación") 
    validacion_resumen = Column(JSON, comment="JSON con resumen de validación (totales, etc.)")
    
    # Relaciones
    archivos = relationship("ArchivoCargado", back_populates="migracion", 
                          cascade="all, delete-orphan")
    campos = relationship("CampoMapeado", back_populates="migracion",
                        cascade="all, delete-orphan")
    logs = relationship("MigracionLog", back_populates="migracion",
                       cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<MigracionMetadata(id={self.id}, tabla='{self.nombre_tabla}', estado='{self.estado}')>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el modelo a diccionario para JSON"""
        return {
            'id': self.id,
            'nombre_tabla': self.nombre_tabla,
            'nombre_original_archivo': self.nombre_original_archivo,
            'tipo_archivo': self.tipo_archivo,
            'tamanio_bytes': self.tamanio_bytes,
            'total_registros': self.total_registros,
            'estado': self.estado,
            'usuario_id': self.usuario_id,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'fecha_actualizacion': self.fecha_actualizacion.isoformat() if self.fecha_actualizacion else None,
            'mensaje_error': self.mensaje_error,
            'tiempo_procesamiento_segundos': self.tiempo_procesamiento_segundos,
            'validacion_errores': self.validacion_errores,
            'validacion_advertencias': self.validacion_advertencias,
            'validacion_resumen': self.validacion_resumen
        }


class ArchivoCargado(Base):
    """
    Almacena metadata detallada de los archivos cargados.
    
    Registra información técnica del archivo para auditoría y debugging.
    """
    __tablename__ = "archivos_cargados"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    migracion_id = Column(Integer, ForeignKey('migraciones_metadata.id'), 
                         nullable=False, index=True)
    nombre_archivo = Column(String(500), nullable=False,
                          comment="Nombre del archivo original")
    ruta_temporal = Column(String(1000), 
                         comment="Ruta temporal donde se guardó el archivo")
    hash_archivo = Column(String(64), index=True,
                        comment="SHA256 hash para detectar duplicados")
    extension = Column(String(10), comment="Extensión del archivo (.xlsx, .csv, etc)")
    mime_type = Column(String(100), comment="MIME type del archivo")
    encoding = Column(String(50), comment="Codificación del archivo (utf-8, latin1, etc)")
    separador = Column(String(10), comment="Separador para archivos CSV")
    tiene_cabecera = Column(Boolean, default=True,
                          comment="Si el archivo tiene fila de cabeceras")
    hojas_excel = Column(Text, comment="JSON con nombres de hojas de Excel")
    fecha_carga = Column(DateTime, default=func.now(), index=True)
    
    # Relaciones
    migracion = relationship("MigracionMetadata", back_populates="archivos")
    
    def __repr__(self):
        return f"<ArchivoCargado(id={self.id}, archivo='{self.nombre_archivo}')>"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'migracion_id': self.migracion_id,
            'nombre_archivo': self.nombre_archivo,
            'extension': self.extension,
            'mime_type': self.mime_type,
            'encoding': self.encoding,
            'separador': self.separador,
            'tiene_cabecera': self.tiene_cabecera,
            'hojas_excel': json.loads(self.hojas_excel) if self.hojas_excel else None,
            'fecha_carga': self.fecha_carga.isoformat() if self.fecha_carga else None
        }


class ConexionExterna(Base):
    """
    Almacena configuraciones de conexiones a bases de datos externas.
    
    Las contraseñas se almacenan encriptadas con AES-256.
    IMPORTANTE: Nunca exponer las contraseñas en APIs.
    """
    __tablename__ = "conexiones_externas"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre_conexion = Column(String(255), nullable=False, unique=True,
                            comment="Nombre descriptivo de la conexión")
    tipo_motor = Column(String(50), nullable=False, index=True,
                       comment="Tipo: 'mssql', 'mysql', 'postgresql', 'oracle', 'sqlite'")
    host = Column(String(255), nullable=False, comment="Host o IP del servidor")
    puerto = Column(Integer, nullable=False, comment="Puerto de conexión")
    usuario = Column(String(255), nullable=False, comment="Usuario de la BD")
    password_encriptada = Column(LargeBinary(500), 
                                comment="Password encriptada con AES-256")
    nombre_base_datos = Column(String(255), comment="Nombre de la base de datos")
    esquema = Column(String(100), comment="Esquema por defecto")
    ssl_habilitado = Column(Boolean, default=False, comment="Si usa SSL/TLS")
    parametros_adicionales = Column(Text, 
                                   comment="JSON con parámetros adicionales")
    estado = Column(String(50), default='activa', index=True,
                   comment="Estado: 'activa', 'inactiva', 'error'")
    ultima_conexion = Column(DateTime, comment="Última vez que se conectó exitosamente")
    mensaje_ultimo_error = Column(Text, comment="Último error de conexión si existe")
    usuario_creador = Column(Integer, ForeignKey('Usuarios.codigo'), nullable=False,
                            comment="Usuario que creó la conexión")
    fecha_creacion = Column(DateTime, default=func.now(), index=True)
    fecha_actualizacion = Column(DateTime, onupdate=func.now())
    
    def __repr__(self):
        return f"<ConexionExterna(id={self.id}, nombre='{self.nombre_conexion}', motor='{self.tipo_motor}')>"
    
    def to_dict(self, incluir_credenciales: bool = False) -> Dict[str, Any]:
        """
        Convierte a diccionario.
        
        Args:
            incluir_credenciales: Si True, incluye usuario (pero NUNCA password)
        """
        data = {
            'id': self.id,
            'nombre_conexion': self.nombre_conexion,
            'tipo_motor': self.tipo_motor,
            'host': self.host,
            'puerto': self.puerto,
            'nombre_base_datos': self.nombre_base_datos,
            'esquema': self.esquema,
            'ssl_habilitado': self.ssl_habilitado,
            'estado': self.estado,
            'ultima_conexion': self.ultima_conexion.isoformat() if self.ultima_conexion else None,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None
        }
        
        if incluir_credenciales:
            data['usuario'] = self.usuario
            # NUNCA incluir password en el diccionario
            
        return data


class MigracionLog(Base):
    """
    Registro de auditoría de todas las operaciones de migraciones.
    
    Almacena un log completo de quién hizo qué, cuándo y con qué resultado.
    Esencial para compliance y debugging.
    """
    __tablename__ = "migraciones_log"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    migracion_id = Column(Integer, ForeignKey('migraciones_metadata.id'), 
                         index=True, comment="Migración relacionada (puede ser NULL)")
    usuario_id = Column(Integer, nullable=True, index=True)
    operacion = Column(String(100), nullable=False, index=True,
                      comment="Operación: 'crear', 'leer', 'actualizar', 'eliminar', 'exportar', 'conectar'")
    tabla_afectada = Column(String(255), index=True,
                          comment="Nombre de la tabla afectada")
    registros_afectados = Column(Integer, default=0,
                                comment="Cantidad de registros modificados")
    detalles = Column(Text, comment="JSON con información adicional")
    ip_origen = Column(String(50), comment="IP desde donde se hizo la operación")
    user_agent = Column(String(500), comment="User agent del navegador")
    duracion_ms = Column(Integer, comment="Duración de la operación en milisegundos")
    estado = Column(String(50), nullable=False, index=True,
                   comment="Estado: 'exito', 'error', 'cancelado', 'parcial'")
    mensaje = Column(Text, comment="Mensaje descriptivo o de error")
    fecha_operacion = Column(DateTime, default=func.now(), index=True)
    
    # Relaciones
    migracion = relationship("MigracionMetadata", back_populates="logs")
    
    def __repr__(self):
        return f"<MigracionLog(id={self.id}, operacion='{self.operacion}', estado='{self.estado}')>"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'migracion_id': self.migracion_id,
            'usuario_id': self.usuario_id,
            'operacion': self.operacion,
            'tabla_afectada': self.tabla_afectada,
            'registros_afectados': self.registros_afectados,
            'detalles': json.loads(self.detalles) if self.detalles else None,
            'duracion_ms': self.duracion_ms,
            'estado': self.estado,
            'mensaje': self.mensaje,
            'fecha_operacion': self.fecha_operacion.isoformat() if self.fecha_operacion else None
        }


class CampoMapeado(Base):
    """
    Mapeo de campos entre origen y destino en migraciones.
    
    Útil para:
    - Recordar cómo se mapearon los campos
    - Replicar migraciones similares
    - Documentar transformaciones aplicadas
    """
    __tablename__ = "campos_mapeados"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    migracion_id = Column(Integer, ForeignKey('migraciones_metadata.id'),
                         nullable=False, index=True)
    campo_origen = Column(String(255), nullable=False,
                         comment="Nombre del campo en el origen")
    tipo_origen = Column(String(100), comment="Tipo de dato en el origen")
    campo_destino = Column(String(255), nullable=False,
                          comment="Nombre del campo en la tabla destino")
    tipo_destino = Column(String(100), nullable=False,
                         comment="Tipo de dato en SQL Server")
    transformacion = Column(Text, 
                          comment="JSON con reglas de transformación aplicadas")
    es_clave_primaria = Column(Boolean, default=False,
                              comment="Si este campo es primary key")
    es_nullable = Column(Boolean, default=True,
                        comment="Si permite valores NULL")
    valor_por_defecto = Column(String(500), 
                              comment="Valor por defecto si aplica")
    longitud_maxima = Column(Integer, comment="Longitud máxima para VARCHAR")
    precision_decimal = Column(Integer, comment="Precisión para DECIMAL")
    escala_decimal = Column(Integer, comment="Escala para DECIMAL")
    
    # Relaciones
    migracion = relationship("MigracionMetadata", back_populates="campos")
    
    def __repr__(self):
        return f"<CampoMapeado(id={self.id}, origen='{self.campo_origen}', destino='{self.campo_destino}')>"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'migracion_id': self.migracion_id,
            'campo_origen': self.campo_origen,
            'tipo_origen': self.tipo_origen,
            'campo_destino': self.campo_destino,
            'tipo_destino': self.tipo_destino,
            'transformacion': json.loads(self.transformacion) if self.transformacion else None,
            'es_clave_primaria': self.es_clave_primaria,
            'es_nullable': self.es_nullable,
            'valor_por_defecto': self.valor_por_defecto,
            'longitud_maxima': self.longitud_maxima,
            'precision_decimal': self.precision_decimal,
            'escala_decimal': self.escala_decimal
        }


# Funciones de utilidad

def crear_log_migracion(
    db,
    usuario_id: int,
    operacion: str,
    estado: str,
    mensaje: str,
    migracion_id: Optional[int] = None,
    tabla_afectada: Optional[str] = None,
    registros_afectados: int = 0,
    duracion_ms: Optional[int] = None,
    detalles: Optional[Dict[str, Any]] = None,
    ip_origen: Optional[str] = None,
    user_agent: Optional[str] = None
) -> MigracionLog:
    """
    Crea un registro de log de forma simplificada.
    
    Args:
        db: Sesión de SQLAlchemy
        usuario_id: ID del usuario que realiza la operación
        operacion: Tipo de operación ('crear', 'leer', etc.)
        estado: Estado de la operación ('exito', 'error', etc.)
        mensaje: Mensaje descriptivo
        ... (parámetros opcionales)
    
    Returns:
        El objeto MigracionLog creado
    """
    log = MigracionLog(
        migracion_id=migracion_id,
        usuario_id=usuario_id,
        operacion=operacion,
        tabla_afectada=tabla_afectada,
        registros_afectados=registros_afectados,
        detalles=json.dumps(detalles) if detalles else None,
        ip_origen=ip_origen,
        user_agent=user_agent,
        duracion_ms=duracion_ms,
        estado=estado,
        mensaje=mensaje
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def obtener_estadisticas_migraciones(db, usuario_id: Optional[int] = None) -> Dict[str, Any]:
    """
    Obtiene estadísticas generales de migraciones.
    
    Args:
        db: Sesión de SQLAlchemy
        usuario_id: Si se especifica, filtra por usuario
    
    Returns:
        Diccionario con estadísticas
    """
    query = db.query(MigracionMetadata)
    
    if usuario_id:
        query = query.filter(MigracionMetadata.usuario_id == usuario_id)
    
    total = query.count()
    completadas = query.filter(MigracionMetadata.estado == 'completado').count()
    errores = query.filter(MigracionMetadata.estado == 'error').count()
    procesando = query.filter(MigracionMetadata.estado == 'procesando').count()
    
    # Total de registros migrados
    total_registros = db.query(func.sum(MigracionMetadata.total_registros)).scalar() or 0
    
    # Espacio usado (aproximado)
    espacio_usado_bytes = db.query(func.sum(MigracionMetadata.tamanio_bytes)).scalar() or 0
    espacio_usado_mb = round(espacio_usado_bytes / (1024 * 1024), 2)
    
    return {
        'total_migraciones': total,
        'completadas': completadas,
        'errores': errores,
        'procesando': procesando,
        'total_registros': total_registros,
        'espacio_usado_mb': espacio_usado_mb
    }


class ExportacionBD(Base):
    """
    Almacena información sobre exportaciones de tablas locales a bases de datos externas.
    
    Esta tabla registra cuando se exportan datos desde la BD local hacia
    otra base de datos (tercera BD en el flujo de migración).
    """
    __tablename__ = "exportaciones_bd"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    migracion_id = Column(Integer, ForeignKey('migraciones_metadata.id'),
                         nullable=True, index=True,
                         comment="ID de la migración original (si aplica)")
    tabla_origen_local = Column(String(255), nullable=False, index=True,
                               comment="Nombre de la tabla en BD local")
    tabla_destino = Column(String(255), nullable=False,
                          comment="Nombre de la tabla en BD destino")
    
    # Información de conexión (sin password por seguridad)
    tipo_motor_destino = Column(String(50), nullable=False,
                               comment="Tipo: 'mssql', 'mysql', 'postgresql'")
    host_destino = Column(String(255), nullable=False,
                         comment="Host de la BD destino")
    puerto_destino = Column(Integer, nullable=False,
                           comment="Puerto de la BD destino")
    nombre_bd_destino = Column(String(255), nullable=False,
                              comment="Nombre de la BD destino")
    esquema_destino = Column(String(100), default='dbo',
                            comment="Esquema en BD destino")
    
    # Datos de la exportación
    modo_exportacion = Column(String(50), nullable=False,
                             comment="Modo: 'crear', 'reemplazar', 'append'")
    total_registros_exportados = Column(Integer, default=0,
                                       comment="Total de registros exportados")
    total_columnas = Column(Integer, default=0,
                           comment="Total de columnas exportadas")
    chunk_size = Column(Integer, default=1000,
                       comment="Tamaño de chunks usado")
    
    # Estado y auditoría
    estado = Column(String(50), default='procesando', index=True,
                   comment="Estado: 'procesando', 'completado', 'error'")
    usuario_id = Column(Integer, nullable=True,
                       comment="Usuario que ejecutó la exportación")
    fecha_exportacion = Column(DateTime, default=func.now(), index=True,
                              comment="Fecha y hora de exportación")
    tiempo_procesamiento_segundos = Column(Float,
                                          comment="Tiempo que tomó exportar")
    mensaje_error = Column(Text, comment="Mensaje de error si falla")
    
    # Metadata adicional
    parametros_adicionales = Column(JSON,
                                   comment="Parámetros adicionales en JSON")
    
    def __repr__(self):
        return f"<ExportacionBD(id={self.id}, tabla='{self.tabla_origen_local}' -> '{self.tabla_destino}', estado='{self.estado}')>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el modelo a diccionario para JSON"""
        return {
            'id': self.id,
            'migracion_id': self.migracion_id,
            'tabla_origen_local': self.tabla_origen_local,
            'tabla_destino': self.tabla_destino,
            'tipo_motor_destino': self.tipo_motor_destino,
            'host_destino': self.host_destino,
            'puerto_destino': self.puerto_destino,
            'nombre_bd_destino': self.nombre_bd_destino,
            'esquema_destino': self.esquema_destino,
            'modo_exportacion': self.modo_exportacion,
            'total_registros_exportados': self.total_registros_exportados,
            'total_columnas': self.total_columnas,
            'chunk_size': self.chunk_size,
            'estado': self.estado,
            'usuario_id': self.usuario_id,
            'fecha_exportacion': self.fecha_exportacion.isoformat() if self.fecha_exportacion else None,
            'tiempo_procesamiento_segundos': self.tiempo_procesamiento_segundos,
            'mensaje_error': self.mensaje_error,
            'parametros_adicionales': self.parametros_adicionales
        }
