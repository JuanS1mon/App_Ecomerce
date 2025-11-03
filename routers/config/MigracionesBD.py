"""
Router de Migración entre Bases de Datos (Multi-Motor)
=======================================================

Endpoints para conectar a bases de datos externas y migrar datos.
Soporta: SQL Server, PostgreSQL, MySQL, Oracle.

Autor: Sistema SQL App
Fecha: 18 de octubre de 2025
Versión: 2.0 (Multi-Motor)
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
import logging

from db.database import get_db
from db.schemas.config.userdb import UserDB
from security.auth_middleware import require_role_api
from utils.db_connector import DatabaseConnectorFactory, get_connector

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Router
router = APIRouter(
    prefix="/migraciones/bd",
    tags=["Migraciones BD Multi-Motor"]
)


# ==================== MODELOS PYDANTIC ====================

class ConexionTestRequest(BaseModel):
    """Request para probar conexión"""
    tipo_motor: str = Field(default="mssql", description="Motor de BD: mssql, postgresql, mysql, oracle")
    host: str = Field(..., description="IP o hostname del servidor")
    puerto: int = Field(default=1433, description="Puerto de conexión")
    usuario: str = Field(..., description="Usuario de la BD")
    password: str = Field(..., description="Contraseña")
    nombre_base_datos: str = Field(..., description="Nombre de la base de datos")
    
    class Config:
        json_schema_extra = {
            "example": {
                "tipo_motor": "mssql",
                "host": "192.168.1.100",
                "puerto": 1433,
                "usuario": "sa",
                "password": "MyPassword123",
                "nombre_base_datos": "Ventas2024"
            }
        }


class TablaPreviewRequest(BaseModel):
    """Request para obtener preview de tabla"""
    tipo_motor: str = Field(default="mssql", description="Motor de BD: mssql, postgresql, mysql, oracle")
    host: str
    puerto: int = 1433
    usuario: str
    password: str
    nombre_base_datos: str
    tabla: str = Field(..., description="Nombre de la tabla")
    esquema: str = Field(default="dbo", description="Esquema de la tabla")
    limite: int = Field(default=100, ge=1, le=1000, description="Cantidad de filas (máx 1000)")


class TablaInfoRequest(BaseModel):
    """Request para obtener información de tabla"""
    tipo_motor: str = Field(default="mssql", description="Motor de BD: mssql, postgresql, mysql, oracle")
    host: str
    puerto: int = 1433
    usuario: str
    password: str
    nombre_base_datos: str
    tabla: str
    esquema: str = "dbo"


# ==================== ENDPOINTS ====================

@router.post("/test-conexion", summary="Probar Conexión a BD Externa")
async def test_conexion(
    request: ConexionTestRequest,
    current_user: UserDB = Depends(require_role_api(["admin", "usuario"]))
):
    """
    🔌 Prueba conexión a una base de datos externa (Multi-Motor).
    
    **Soporta:** SQL Server, PostgreSQL, MySQL, Oracle
    **No guarda la conexión**, solo verifica que sea válida.
    
    Returns:
        - exito: bool
        - mensaje: str con detalles de la conexión
        - version_servidor: str con versión del motor
        - motor: str tipo de motor conectado
    """
    try:
        logger.info(f"👤 Usuario {current_user.usuario} probando conexión {request.tipo_motor} a {request.host}")
        
        # Verificar si el motor está disponible
        disponible, msg_disponibilidad = DatabaseConnectorFactory.is_motor_available(request.tipo_motor)
        if not disponible:
            raise HTTPException(
                status_code=400,
                detail=f"Motor '{request.tipo_motor}' no disponible: {msg_disponibilidad}"
            )
        
        # Crear conector usando factory
        connector = get_connector(
            tipo_motor=request.tipo_motor,
            host=request.host,
            port=request.puerto,
            user=request.usuario,
            password=request.password,
            database=request.nombre_base_datos
        )
        
        # Probar conexión
        exito, mensaje = connector.test_connection()
        
        if not exito:
            return JSONResponse(
                status_code=400,
                content={
                    "exito": False,
                    "mensaje": mensaje,
                    "error": "No se pudo conectar a la base de datos"
                }
            )
        
        return {
            "exito": True,
            "mensaje": "Conexión exitosa",
            "version_servidor": mensaje,
            "tipo_motor": request.tipo_motor,
            "host": request.host,
            "puerto": request.puerto,
            "base_datos": request.nombre_base_datos
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error en test_conexion: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al probar conexión: {str(e)}")


@router.post("/listar-tablas", summary="Listar Tablas de BD Externa")
async def listar_tablas(
    request: ConexionTestRequest,
    include_row_count: bool = True,
    current_user: UserDB = Depends(require_role_api(["admin", "usuario"]))
):
    """
    📋 Lista todas las tablas de una base de datos SQL Server externa.
    
    Args:
        request: Datos de conexión
        include_row_count: Si incluir conteo de filas (puede ser lento)
    
    Returns:
        - success: bool
        - tablas: List[Dict] con información de cada tabla
        - total: int cantidad de tablas
    """
    try:
        logger.info(f"👤 Usuario {current_user.usuario} listando tablas de {request.tipo_motor}:{request.host}/{request.nombre_base_datos}")
        
        # Crear conector usando factory
        connector = get_connector(
            tipo_motor=request.tipo_motor,
            host=request.host,
            port=request.puerto,
            user=request.usuario,
            password=request.password,
            database=request.nombre_base_datos
        )
        
        # Primero probar conexión
        exito, mensaje = connector.test_connection()
        if not exito:
            raise HTTPException(status_code=400, detail=mensaje)
        
        # Listar tablas
        tablas = connector.list_tables(include_row_count=include_row_count)
        
        return {
            "exito": True,
            "tablas": tablas,
            "total_tablas": len(tablas),
            "base_datos": request.nombre_base_datos,
            "tipo_motor": request.tipo_motor,
            "mensaje": f"✅ {len(tablas)} tablas encontradas"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error en listar_tablas: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al listar tablas: {str(e)}")


@router.post("/tabla-info", summary="Obtener Información de Tabla")
async def obtener_info_tabla(
    request: TablaInfoRequest,
    current_user: UserDB = Depends(require_role_api(["admin", "usuario"]))
):
    """
    ℹ️ Obtiene información detallada de una tabla específica.
    
    Returns:
        - esquema: str
        - tabla: str
        - columnas: List[Dict] con info de cada columna
        - total_filas: int cantidad total de registros
    """
    try:
        logger.info(f"👤 Usuario {current_user.usuario} obteniendo info de {request.tipo_motor}:{request.esquema}.{request.tabla}")
        
        connector = get_connector(
            tipo_motor=request.tipo_motor,
            host=request.host,
            port=request.puerto,
            user=request.usuario,
            password=request.password,
            database=request.nombre_base_datos
        )
        
        # Obtener información
        info = connector.get_table_info(table=request.tabla, schema=request.esquema)
        
        return {
            "exito": True,
            **info
        }
        
    except Exception as e:
        logger.error(f"❌ Error en obtener_info_tabla: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al obtener información: {str(e)}")


@router.post("/tabla-preview", summary="Preview de Datos de Tabla")
async def preview_tabla(
    request: TablaPreviewRequest,
    current_user: UserDB = Depends(require_role_api(["admin", "usuario"]))
):
    """
    👁️ Obtiene preview de los primeros N registros de una tabla.
    
    Args:
        request: Datos de conexión + tabla + límite
    
    Returns:
        - columnas: List[str] nombres de columnas
        - tipos: Dict[str, str] tipo de dato de cada columna
        - filas: List[List] datos (como lista de listas para JSON)
        - total_filas_preview: int cantidad de filas en el preview
    """
    try:
        logger.info(f"👤 Usuario {current_user.usuario} obteniendo preview de {request.tipo_motor}:{request.esquema}.{request.tabla}")
        
        connector = get_connector(
            tipo_motor=request.tipo_motor,
            host=request.host,
            port=request.puerto,
            user=request.usuario,
            password=request.password,
            database=request.nombre_base_datos
        )
        
        # Obtener preview
        df = connector.get_table_preview(
            table=request.tabla,
            schema=request.esquema,
            limit=request.limite
        )
        
        # Obtener tipos de columnas
        tipos = connector.get_column_types(table=request.tabla, schema=request.esquema)
        
        # Convertir DataFrame a formato JSON amigable
        columnas = df.columns.tolist()
        
        # Convertir valores NaN y NaT a None para JSON
        filas = df.fillna("NULL").values.tolist()
        
        return {
            "exito": True,
            "tabla": f"{request.esquema}.{request.tabla}",
            "columnas": columnas,
            "tipos": tipos,
            "filas": filas,
            "total_filas_preview": len(filas),
            "limite_aplicado": request.limite
        }
        
    except Exception as e:
        logger.error(f"❌ Error en preview_tabla: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al obtener preview: {str(e)}")


# ========== PASO 2: IMPORTAR DATOS A BD LOCAL ==========

class ImportacionRequest(BaseModel):
    """Request para importar tabla de BD externa a BD local"""
    tipo_motor: str = Field(..., description="Tipo de motor (mssql, mysql, postgresql)")
    host: str = Field(..., description="Host del servidor")
    puerto: int = Field(..., description="Puerto de conexión")
    usuario: str = Field(..., description="Usuario de la base de datos")
    password: str = Field(..., description="Contraseña del usuario")
    nombre_base_datos: str = Field(..., description="Nombre de la base de datos")
    tabla: str = Field(..., description="Nombre de la tabla a importar")
    esquema: str = Field(default="dbo", description="Esquema de la tabla")
    nombre_tabla_destino: Optional[str] = Field(None, description="Nombre de la tabla en BD local (opcional)")
    chunk_size: int = Field(default=1000, description="Tamaño de chunks para importación")


@router.post("/importar", summary="Importar Tabla a BD Local")
async def importar_tabla(
    request: ImportacionRequest,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(require_role_api(["admin", "usuario"]))
):
    """
    📥 PASO 2: Importar tabla de BD externa a BD local
    
    Proceso:
    1. Conectar a BD externa
    2. Extraer esquema y datos
    3. Crear tabla en BD local con estructura idéntica
    4. Insertar datos en chunks
    5. Registrar migración en metadata
    
    Returns:
        - exito: bool
        - migracion_id: ID del registro de migración
        - tabla_destino: Nombre de la tabla creada
        - registros_importados: Cantidad de registros
        - tiempo_total: Tiempo de procesamiento
    """
    import time
    from sqlalchemy import Table, Column, MetaData, Integer, String, Float, DateTime, Boolean, Text
    from sqlalchemy.types import VARCHAR, NVARCHAR, INTEGER, FLOAT, DATETIME, BOOLEAN, TEXT
    from datetime import datetime
    from db.database import engine, SQLALCHEMY_DATABASE_URL
    
    logger.info(f"📥 Iniciando importación de {request.esquema}.{request.tabla}")
    logger.info(f"🎯 BD ORIGEN (Externa): {request.tipo_motor}://{request.host}:{request.puerto}/{request.nombre_base_datos}")
    logger.info(f"🎯 BD DESTINO (Principal): {SQLALCHEMY_DATABASE_URL}")
    
    inicio = time.time()
    
    try:
        # 1. Validar tipo de motor
        disponible, msg = DatabaseConnectorFactory.is_motor_available(request.tipo_motor)
        if not disponible:
            raise HTTPException(
                status_code=400,
                detail=f"Motor '{request.tipo_motor}' no disponible: {msg}"
            )
        
        # 2. Crear connector a BD externa usando factory
        connector = get_connector(
            tipo_motor=request.tipo_motor,
            host=request.host,
            port=request.puerto,
            user=request.usuario,
            password=request.password,
            database=request.nombre_base_datos
        )
        
        # 3. Obtener info de la tabla origen
        info_tabla = connector.get_table_info(table=request.tabla, schema=request.esquema)
        columnas_origen = info_tabla["columnas"]
        total_filas = info_tabla["total_filas"]
        
        logger.info(f"📊 Tabla origen: {len(columnas_origen)} columnas, {total_filas} registros")
        
        # 4. Definir nombre de tabla destino
        nombre_tabla_destino = request.nombre_tabla_destino or f"migrado_{request.tabla}"
        
        # 5. Mapear tipos de SQL Server a SQLAlchemy
        def map_sqlserver_type(tipo_sqlserver: str):
            """Mapea tipos de SQL Server a tipos de SQLAlchemy"""
            tipo_upper = tipo_sqlserver.upper()
            
            if "INT" in tipo_upper or "BIGINT" in tipo_upper or "SMALLINT" in tipo_upper:
                return Integer
            elif "DECIMAL" in tipo_upper or "NUMERIC" in tipo_upper or "MONEY" in tipo_upper:
                return Float
            elif "FLOAT" in tipo_upper or "REAL" in tipo_upper:
                return Float
            elif "VARCHAR" in tipo_upper:
                return VARCHAR(255)
            elif "NVARCHAR" in tipo_upper:
                return NVARCHAR(255)
            elif "TEXT" in tipo_upper or "NTEXT" in tipo_upper:
                return TEXT
            elif "CHAR" in tipo_upper or "NCHAR" in tipo_upper:
                return String(50)
            elif "DATE" in tipo_upper or "TIME" in tipo_upper:
                return DateTime
            elif "BIT" in tipo_upper:
                return Boolean
            else:
                return String(255)
        
        # 6. Crear tabla dinámica en BD PRINCIPAL (local)
        metadata = MetaData()
        columnas = [Column('id', Integer, primary_key=True, autoincrement=True)]
        
        for col in columnas_origen:
            tipo_sqlalchemy = map_sqlserver_type(col["tipo"])
            columnas.append(Column(col["nombre"], tipo_sqlalchemy, nullable=True))
        
        tabla_destino = Table(nombre_tabla_destino, metadata, *columnas)
        
        # ===== VERIFICAR SI LA TABLA YA EXISTE USANDO SQL DIRECTO =====
        from sqlalchemy import text
        
        verificacion_query = text("""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_SCHEMA = 'dbo' 
            AND TABLE_NAME = :table_name
            AND TABLE_TYPE = 'BASE TABLE'
        """)
        
        with engine.connect() as conn:
            result = conn.execute(verificacion_query, {"table_name": nombre_tabla_destino})
            tabla_ya_existe = result.scalar() > 0
        
        if tabla_ya_existe:
            # Tabla ya existe - obtener información usando SQL directo
            logger.warning(f"⚠️ La tabla '{nombre_tabla_destino}' YA EXISTE en BD PRINCIPAL")
            
            # Obtener columnas existentes
            columnas_query = text("""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = 'dbo' 
                AND TABLE_NAME = :table_name
                ORDER BY ORDINAL_POSITION
            """)
            with engine.connect() as conn:
                result = conn.execute(columnas_query, {"table_name": nombre_tabla_destino})
                columnas_existentes = [row[0] for row in result.fetchall()]
            
            # Contar registros existentes
            count_query = text(f"SELECT COUNT(*) FROM [{nombre_tabla_destino}]")
            with engine.connect() as conn:
                registros_existentes = conn.execute(count_query).scalar()
            
            logger.info(f"📋 Tabla existente: {len(columnas_existentes)} columnas, {registros_existentes} registros")
            
            raise HTTPException(
                status_code=400,
                detail=f"⚠️ La tabla con el nombre '{nombre_tabla_destino}' ya existe en la BD Principal (tecnolarUnificado). "
                       f"Contiene {registros_existentes:,} registros y {len(columnas_existentes)} columnas. "
                       f"Por favor, usa un nombre diferente o elimina la tabla existente primero."
            )
        
        # ===== CREAR TABLA USANDO DDL DIRECTO (sin metadata.create_all) =====
        logger.info(f"🔨 Creando tabla '{nombre_tabla_destino}' en BD PRINCIPAL...")
        
        # Generar DDL manualmente para evitar error HY104
        columnas_ddl = ["id INT IDENTITY(1,1) PRIMARY KEY"]
        
        for col in columnas_origen:
            tipo_sql = col["tipo"].upper()
            nombre_col = col["nombre"]
            
            # Mapear tipos a SQL Server DDL
            if "INT" in tipo_sql and "BIGINT" not in tipo_sql:
                tipo_ddl = "INT"
            elif "BIGINT" in tipo_sql:
                tipo_ddl = "BIGINT"
            elif "DECIMAL" in tipo_sql or "NUMERIC" in tipo_sql:
                tipo_ddl = "DECIMAL(18,2)"
            elif "FLOAT" in tipo_sql or "REAL" in tipo_sql:
                tipo_ddl = "FLOAT"
            elif "VARCHAR" in tipo_sql:
                tipo_ddl = "VARCHAR(255)"
            elif "NVARCHAR" in tipo_sql:
                tipo_ddl = "NVARCHAR(255)"
            elif "TEXT" in tipo_sql:
                tipo_ddl = "TEXT"
            elif "NTEXT" in tipo_sql:
                tipo_ddl = "NTEXT"
            elif "CHAR" in tipo_sql and "NCHAR" not in tipo_sql:
                tipo_ddl = "CHAR(50)"
            elif "NCHAR" in tipo_sql:
                tipo_ddl = "NCHAR(50)"
            elif "DATE" in tipo_sql or "TIME" in tipo_sql:
                tipo_ddl = "DATETIME"
            elif "BIT" in tipo_sql:
                tipo_ddl = "BIT"
            else:
                tipo_ddl = "NVARCHAR(255)"
            
            columnas_ddl.append(f"[{nombre_col}] {tipo_ddl} NULL")
        
        # Construir SQL como string simple (sin text())
        create_table_sql_string = f"""
            CREATE TABLE [{nombre_tabla_destino}] (
                {', '.join(columnas_ddl)}
            )
        """
        
        # Ejecutar usando raw SQL con engine
        with engine.begin() as conn:
            conn.exec_driver_sql(create_table_sql_string)
        
        logger.info(f"✅ Tabla '{nombre_tabla_destino}' creada en BD PRINCIPAL con DDL directo")
        
        # Verificar nuevamente que la tabla existe
        with engine.connect() as conn:
            result = conn.execute(verificacion_query, {"table_name": nombre_tabla_destino})
            tabla_existe = result.scalar() > 0
        
        if not tabla_existe:
            raise Exception(f"❌ La tabla '{nombre_tabla_destino}' no se creó correctamente en BD PRINCIPAL")
        
        logger.info(f"✅ Tabla verificada en BD PRINCIPAL")
        
        # 7. Extraer datos de BD EXTERNA y cargar en BD PRINCIPAL
        registros_importados = 0
        chunks_procesados = 0
        
        logger.info(f"🔄 Iniciando extracción de datos de BD EXTERNA...")
        logger.info(f"📥 Origen: {request.tipo_motor}://{request.host}/{request.nombre_base_datos}.{request.esquema}.{request.tabla}")
        logger.info(f"📤 Destino: BD PRINCIPAL → tabla '{nombre_tabla_destino}'")
        
        # IMPORTANTE: Usar conexión directa del engine de BD PRINCIPAL para inserciones masivas
        with engine.begin() as conn:
            for chunk_df in connector.extract_table_complete(
                table=request.tabla,
                schema=request.esquema,
                chunk_size=request.chunk_size
            ):
                chunks_procesados += 1
                registros = chunk_df.to_dict('records')
                
                if registros:
                    # Mostrar primer registro del primer chunk para debug
                    if chunks_procesados == 1:
                        logger.info(f"📄 Primer registro de ejemplo: {list(registros[0].keys())[:5]}")
                    
                    # Insertar usando la conexión directa (más rápido y confiable)
                    result = conn.execute(tabla_destino.insert(), registros)
                    registros_importados += len(registros)
                    logger.info(f"📦 Chunk #{chunks_procesados}: {len(registros)} registros insertados (Total: {registros_importados}/{total_filas})")
                else:
                    logger.warning(f"⚠️ Chunk #{chunks_procesados} vacío, omitiendo...")
        
        logger.info(f"✅ Datos insertados en BD PRINCIPAL: {registros_importados} registros en {chunks_procesados} chunks")
        
        # 8. Calcular tiempo total
        tiempo_total = time.time() - inicio
        
        logger.info(f"🎉 IMPORTACIÓN COMPLETADA EXITOSAMENTE")
        logger.info(f"   📊 Total registros: {registros_importados}")
        logger.info(f"   ⏱️  Tiempo: {tiempo_total:.2f}s")
        logger.info(f"   🎯 BD Principal: {nombre_tabla_destino}")
        
        # 9. Crear registro de migración AL FINAL (cuando todo está completo)
        from db.models.config.migraciones import MigracionMetadata
        
        try:
            migracion = MigracionMetadata(
                nombre_tabla=nombre_tabla_destino,
                nombre_original_archivo=f"{request.esquema}.{request.tabla}",
                tipo_archivo="BD_EXTERNA",
                tamanio_bytes=0,
                total_registros=registros_importados,
                estado="completado",
                usuario_id=current_user.codigo,
                mensaje_error=None,
                tiempo_procesamiento_segundos=round(tiempo_total, 2)
            )
            
            db.add(migracion)
            db.commit()
            db.refresh(migracion)
            
            logger.info(f"✅ Registro de migración creado: ID {migracion.id}")
            migracion_id = migracion.id
        except Exception as e_meta:
            logger.warning(f"⚠️ No se pudo crear registro de migración: {str(e_meta)}")
            migracion_id = None
        
        return {
            "exito": True,
            "mensaje": f"Importación completada exitosamente. Datos guardados en BD Principal: {nombre_tabla_destino}",
            "migracion_id": migracion_id,
            "tabla_origen": f"{request.esquema}.{request.tabla}",
            "tabla_destino": nombre_tabla_destino,
            "bd_destino": "BD Principal (tecnolarUnificado)",
            "registros_importados": registros_importados,
            "tiempo_total_segundos": round(tiempo_total, 2),
            "velocidad_reg_por_seg": round(registros_importados / tiempo_total, 2) if tiempo_total > 0 else 0
        }
        
    except HTTPException as http_exc:
        # Re-lanzar HTTPException con su código de estado original (400 para tabla existente)
        logger.warning(f"⚠️ HTTPException en importar_tabla: {http_exc.detail}")
        raise http_exc
        
    except Exception as e:
        # Otros errores inesperados
        logger.error(f"❌ Error inesperado en importar_tabla: {str(e)}")
        logger.error(f"Tipo de error: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        raise HTTPException(
            status_code=500,
            detail=f"Error inesperado al importar tabla: {str(e)}"
        )


# ========== ENDPOINT: VERIFICAR TABLA IMPORTADA ==========

class VerificarTablaRequest(BaseModel):
    """Request para verificar que una tabla existe en BD Principal (tecnolarUnificado)"""
    nombre_tabla: str = Field(..., description="Nombre de la tabla a verificar en BD Principal")

@router.post("/verificar-tabla", tags=["migraciones-bd"])
def verificar_tabla_importada(
    request: VerificarTablaRequest,
    db: Session = Depends(get_db)
):
    """
    Verifica que una tabla existe en la BD Principal (tecnolarUnificado) y devuelve información básica.
    
    Args:
        request: Datos de la tabla a verificar
        db: Sesión de base de datos
    
    Returns:
        JSON con información de la tabla (nombre, registros, columnas)
    """
    from sqlalchemy import inspect, text
    from db.database import engine
    
    logger.info(f"🔍 Verificando tabla en BD PRINCIPAL: {request.nombre_tabla}")
    
    try:
        # 1. Verificar que la tabla existe en BD Principal usando SQL directo (sin inspector)
        verificacion_query = text("""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_SCHEMA = 'dbo' 
            AND TABLE_NAME = :table_name
            AND TABLE_TYPE = 'BASE TABLE'
        """)
        with engine.connect() as conn:
            result = conn.execute(verificacion_query, {"table_name": request.nombre_tabla})
            tabla_existe = result.scalar() > 0
        
        if not tabla_existe:
            return {
                "exito": False,
                "mensaje": f"❌ La tabla '{request.nombre_tabla}' no existe en la BD Principal (tecnolarUnificado)",
                "nombre_tabla": request.nombre_tabla,
                "bd": "tecnolarUnificado"
            }
        
        # 2. Obtener columnas usando SQL directo (sin inspector para evitar HY104)
        columnas_query = text("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = 'dbo' 
            AND TABLE_NAME = :table_name
            ORDER BY ORDINAL_POSITION
        """)
        
        with engine.connect() as conn:
            result = conn.execute(columnas_query, {"table_name": request.nombre_tabla})
            nombres_columnas = [row[0] for row in result.fetchall()]
        
        # 3. Contar registros
        with engine.connect() as conn:
            result = conn.execute(text(f"SELECT COUNT(*) FROM [{request.nombre_tabla}]"))
            total_registros = result.scalar()
        
        logger.info(f"✅ Tabla verificada en BD PRINCIPAL: {request.nombre_tabla} - {total_registros} registros, {len(nombres_columnas)} columnas")
        
        return {
            "exito": True,
            "mensaje": f"✅ Tabla encontrada en BD Principal: {total_registros:,} registros, {len(nombres_columnas)} columnas",
            "nombre_tabla": request.nombre_tabla,
            "bd": "tecnolarUnificado (BD Principal)",
            "total_registros": total_registros,
            "columnas": nombres_columnas,
            "total_columnas": len(nombres_columnas)
        }
        
    except Exception as e:
        logger.error(f"❌ Error al verificar tabla '{request.nombre_tabla}' en BD PRINCIPAL: {str(e)}")
        
        # Mensaje de error más amigable para el usuario
        error_mensaje = "No se pudo verificar la tabla en BD Principal"
        
        if "HY104" in str(e):
            error_mensaje = "⚠️ Error de conexión con la BD Principal. Por favor, intenta nuevamente."
        elif "Invalid object name" in str(e) or "no existe" in str(e).lower():
            error_mensaje = f"❌ La tabla '{request.nombre_tabla}' no fue encontrada en BD Principal (tecnolarUnificado)"
        elif "permission" in str(e).lower() or "denied" in str(e).lower():
            error_mensaje = "🔒 Sin permisos para acceder a esta tabla en BD Principal"
        else:
            error_mensaje = f"❌ Error al verificar en BD Principal: {str(e)[:100]}"
        
        return {
            "exito": False,
            "mensaje": error_mensaje,
            "nombre_tabla": request.nombre_tabla,
            "bd": "tecnolarUnificado (BD Principal)",
            "error_tecnico": str(e) if len(str(e)) < 200 else str(e)[:200] + "..."
        }


# ========== PASO 3: EXPORTAR A BD EXTERNA ==========

class ExportacionRequest(BaseModel):
    """Request para exportar tabla de BD local a BD externa"""
    tabla_origen_local: str = Field(..., description="Nombre de la tabla en BD local")
    tipo_motor_destino: str = Field(..., description="Tipo de motor destino (mssql, mysql, postgresql)")
    host_destino: str = Field(..., description="Host del servidor destino")
    puerto_destino: int = Field(..., description="Puerto de conexión destino")
    usuario_destino: str = Field(..., description="Usuario de la BD destino")
    password_destino: str = Field(..., description="Contraseña del usuario destino")
    nombre_bd_destino: str = Field(..., description="Nombre de la BD destino")
    tabla_destino: Optional[str] = Field(None, description="Nombre de tabla en destino (opcional)")
    esquema_destino: str = Field(default="dbo", description="Esquema en BD destino")
    modo_exportacion: str = Field(default="crear", description="Modo: crear, reemplazar, append")
    chunk_size: int = Field(default=1000, description="Tamaño de chunks para exportación")


@router.post("/exportar", summary="Exportar Tabla a BD Externa")
async def exportar_tabla(
    request: ExportacionRequest,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(require_role_api(["admin", "usuario"]))
):
    """
    📤 PASO 3: Exportar tabla de BD local a BD externa
    
    Proceso:
    1. Verificar que tabla local existe
    2. Extraer datos de BD local
    3. Conectar a BD destino
    4. Crear/Reemplazar/Append según modo
    5. Insertar datos en chunks
    6. Registrar exportación en ExportacionBD
    
    Modos de exportación:
    - crear: Crea nueva tabla (falla si existe)
    - reemplazar: Elimina y recrea tabla
    - append: Agrega datos a tabla existente
    
    Returns:
        - exito: bool
        - exportacion_id: ID del registro de exportación
        - tabla_origen: Nombre de la tabla local
        - tabla_destino: Nombre de la tabla en BD destino
        - registros_exportados: Cantidad de registros
        - tiempo_total: Tiempo de procesamiento
    """
    import time
    from sqlalchemy import Table, MetaData, inspect, text
    from datetime import datetime, date
    
    logger.info(f"📤 Iniciando exportación de '{request.tabla_origen_local}'")
    logger.info(f"   Motor destino: {request.tipo_motor_destino}")
    logger.info(f"   Host: {request.host_destino}:{request.puerto_destino}")
    logger.info(f"   BD: {request.nombre_bd_destino}")
    logger.info(f"   Esquema: {request.esquema_destino}")
    logger.info(f"   Tabla destino: {request.tabla_destino}")
    logger.info(f"   Modo: {request.modo_exportacion}")
    logger.info(f"   Chunk size: {request.chunk_size}")
    
    inicio = time.time()
    exportacion = None
    
    try:
        # 1. Validar tipo de motor
        disponible, msg_disponibilidad = DatabaseConnectorFactory.is_motor_available(request.tipo_motor_destino)
        if not disponible:
            raise HTTPException(
                status_code=400,
                detail=f"Motor '{request.tipo_motor_destino}' no disponible: {msg_disponibilidad}"
            )
        
        # 2. Validar modo de exportación y normalizar a español
        modos_validos = {
            "crear": "crear",
            "create": "crear",
            "reemplazar": "reemplazar", 
            "replace": "reemplazar",
            "append": "append",
            "agregar": "append"
        }
        
        modo_normalizado = request.modo_exportacion.lower()
        if modo_normalizado not in modos_validos:
            raise HTTPException(
                status_code=400,
                detail=f"Modo '{request.modo_exportacion}' inválido. Opciones: create, replace, append"
            )
        
        # Normalizar el modo a español interno
        modo_exportacion_normalizado = modos_validos[modo_normalizado]
        logger.info(f"✅ Modo de exportación: '{request.modo_exportacion}' → '{modo_exportacion_normalizado}'")
        
        # 3. Verificar que tabla local existe usando SQL directo
        from db.database import engine
        
        # Usar SQL directo para evitar el error de NVARCHAR(max)
        verificacion_query = text("""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_SCHEMA = 'dbo' 
            AND TABLE_NAME = :table_name
            AND TABLE_TYPE = 'BASE TABLE'
        """)
        with engine.connect() as conn:
            result = conn.execute(verificacion_query, {"table_name": request.tabla_origen_local})
            tabla_existe = result.scalar() > 0
        
        if not tabla_existe:
            raise HTTPException(
                status_code=404,
                detail=f"Tabla '{request.tabla_origen_local}' no existe en BD local"
            )
        
        logger.info(f"✅ Tabla local '{request.tabla_origen_local}' encontrada")
        
        # 4. Obtener metadata de tabla local usando SQL directo (evita error NVARCHAR(max))
        with engine.connect() as conn:
            # Obtener información de columnas
            columnas_query = text("""
                SELECT 
                    COLUMN_NAME,
                    DATA_TYPE,
                    CHARACTER_MAXIMUM_LENGTH,
                    IS_NULLABLE
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_NAME = :table_name
                AND TABLE_SCHEMA = 'dbo'
                ORDER BY ORDINAL_POSITION
            """)
            
            resultado_cols = conn.execute(columnas_query, {"table_name": request.tabla_origen_local})
            columnas_info = resultado_cols.fetchall()
            total_columnas = len(columnas_info)
            
            # Contar registros
            resultado_count = conn.execute(text(f"SELECT COUNT(*) FROM [{request.tabla_origen_local}]"))
            total_registros = resultado_count.scalar()
        
        logger.info(f"📊 Tabla local: {total_columnas} columnas, {total_registros} registros")
        
        # Crear lista de columnas para usarla después
        columnas_local = []
        for col_info in columnas_info:
            col_dict = {
                'name': col_info[0],
                'type': col_info[1],
                'max_length': col_info[2],
                'nullable': col_info[3] == 'YES'
            }
            columnas_local.append(col_dict)
        
        logger.info(f"📋 Columnas detectadas: {[c['name'] for c in columnas_local]}")
        
        # 5. Definir nombre de tabla destino
        nombre_tabla_destino = request.tabla_destino or request.tabla_origen_local
        
        logger.info(f"� Tabla local: {total_columnas} columnas, {total_registros} registros")
        logger.info(f"🎯 Tabla destino: {nombre_tabla_destino}")
        
        # 7. Conectar a BD destino usando factory
        connector_destino = get_connector(
            tipo_motor=request.tipo_motor_destino,
            host=request.host_destino,
            port=request.puerto_destino,
            user=request.usuario_destino,
            password=request.password_destino,
            database=request.nombre_bd_destino
        )
        
        # Probar conexión
        exito_conexion, mensaje_conexion = connector_destino.test_connection()
        if not exito_conexion:
            raise Exception(f"No se pudo conectar a BD destino: {mensaje_conexion}")
        
        logger.info(f"✅ Conectado a BD destino {request.tipo_motor_destino}: {request.host_destino}")
        
        # 8. Obtener engine de SQLAlchemy para BD destino
        from sqlalchemy import create_engine
        sqlalchemy_url = connector_destino.get_sqlalchemy_url()
        engine_destino = create_engine(sqlalchemy_url)
        
        # Verificar si tabla existe en destino
        from sqlalchemy import inspect as sqla_inspect
        inspector_destino = sqla_inspect(engine_destino)
        
        try:
            tablas_existentes = inspector_destino.get_table_names(schema=request.esquema_destino)
        except Exception as e:
            logger.warning(f"⚠️ No se pudo verificar esquema '{request.esquema_destino}': {str(e)}")
            # Si el esquema no existe, asumir que la tabla tampoco
            tablas_existentes = []
        
        tabla_existe = nombre_tabla_destino in tablas_existentes
        
        if modo_exportacion_normalizado == "crear" and tabla_existe:
            raise Exception(f"Tabla '{nombre_tabla_destino}' ya existe en BD destino. Usa modo 'reemplazar' o 'append'")
        
        if modo_exportacion_normalizado == "reemplazar" and tabla_existe:
            logger.info(f"🗑️ Eliminando tabla existente '{nombre_tabla_destino}'")
            with engine_destino.begin() as conn_dest:
                conn_dest.execute(text(f"DROP TABLE {request.esquema_destino}.{nombre_tabla_destino}"))
        
        # 9. Preparar definición de tabla destino (para create, replace o append)
        from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, Date
        metadata_destino = MetaData(schema=request.esquema_destino)
        
        columnas_nuevas = [Column('id', Integer, primary_key=True, autoincrement=True)]
        
        for col in columnas_local:
            if col['name'].lower() == 'id':  # Skip, ya lo agregamos
                continue
            
            # Mapear tipo de columna basándose en el tipo SQL Server
            tipo_sql = col['type'].upper()
            nombre_col = col['name']
            nullable = col['nullable']
            
            if tipo_sql in ['VARCHAR', 'NVARCHAR', 'CHAR', 'NCHAR', 'TEXT', 'NTEXT']:
                max_len = col['max_length'] if col['max_length'] and col['max_length'] > 0 else 255
                columnas_nuevas.append(Column(nombre_col, String(min(max_len, 4000)), nullable=nullable))
            elif tipo_sql in ['INT', 'INTEGER', 'SMALLINT', 'TINYINT', 'BIGINT']:
                columnas_nuevas.append(Column(nombre_col, Integer, nullable=nullable))
            elif tipo_sql in ['FLOAT', 'REAL', 'NUMERIC', 'DECIMAL', 'MONEY', 'SMALLMONEY']:
                columnas_nuevas.append(Column(nombre_col, Float, nullable=nullable))
            elif tipo_sql in ['DATETIME', 'DATETIME2', 'SMALLDATETIME', 'TIMESTAMP']:
                columnas_nuevas.append(Column(nombre_col, DateTime, nullable=nullable))
            elif tipo_sql in ['DATE']:
                columnas_nuevas.append(Column(nombre_col, Date, nullable=nullable))
            elif tipo_sql in ['BIT']:
                columnas_nuevas.append(Column(nombre_col, Boolean, nullable=nullable))
            else:
                # Default a String para tipos desconocidos
                logger.warning(f"⚠️ Tipo desconocido para columna '{nombre_col}': {tipo_sql}, usando String(255)")
                columnas_nuevas.append(Column(nombre_col, String(255), nullable=True))
        
        # Crear objeto Table (se usará tanto para create como para append)
        tabla_destino_obj = Table(nombre_tabla_destino, metadata_destino, *columnas_nuevas)
        
        # Crear tabla físicamente solo si es necesario
        if not tabla_existe or modo_exportacion_normalizado in ["crear", "reemplazar"]:
            logger.info(f"🏗️ Creando tabla '{nombre_tabla_destino}' en BD destino")
            
            try:
                metadata_destino.create_all(engine_destino)
                logger.info(f"✅ Tabla '{nombre_tabla_destino}' creada en BD destino")
            except Exception as e:
                logger.error(f"❌ Error al crear tabla: {str(e)}")
                raise Exception(f"No se pudo crear tabla en BD destino: {str(e)}")
        
        # 10. Extraer y exportar datos en chunks
        registros_exportados = 0
        
        with engine.connect() as conn_local:
            offset = 0
            chunk_num = 0
            
            while True:
                chunk_num += 1
                
                # Leer chunk de BD local
                query = text(f"""
                    SELECT * FROM [{request.tabla_origen_local}]
                    ORDER BY id
                    OFFSET {offset} ROWS
                    FETCH NEXT {request.chunk_size} ROWS ONLY
                """)
                
                resultado = conn_local.execute(query)
                filas = resultado.fetchall()
                
                logger.info(f"📖 Chunk {chunk_num}: {len(filas)} filas leídas de BD local")
                
                if not filas:
                    logger.info(f"✅ Todos los chunks procesados")
                    break
                
                # Preparar datos para inserción masiva (excluir columna id)
                columnas_insert = [col['name'] for col in columnas_local if col['name'].lower() != 'id']
                
                logger.info(f"📋 Columnas a insertar ({len(columnas_insert)}): {columnas_insert[:5]}{'...' if len(columnas_insert) > 5 else ''}")
                
                # Convertir filas a diccionarios, manejando tipos de datos
                datos_para_insertar = []
                for idx, fila in enumerate(filas):
                    try:
                        # Obtener nombres de columnas disponibles en la fila
                        columnas_disponibles = list(fila._mapping.keys())
                        
                        fila_dict = {}
                        for col_name in columnas_insert:
                            # Buscar la columna en el mapping (case-insensitive)
                            valor = None
                            for col_disponible in columnas_disponibles:
                                if col_disponible.lower() == col_name.lower():
                                    valor = fila._mapping[col_disponible]
                                    break
                            fila_dict[col_name] = valor
                        
                        datos_para_insertar.append(fila_dict)
                        
                        # Log de primera fila para debug
                        if idx == 0:
                            logger.info(f"🔍 Primera fila ejemplo: {list(fila_dict.keys())[:3]} = {list(fila_dict.values())[:3]}")
                            
                    except Exception as e:
                        logger.error(f"❌ Error al procesar fila {idx}: {str(e)}")
                        import traceback
                        logger.error(traceback.format_exc())
                        continue
                
                if not datos_para_insertar:
                    logger.warning(f"⚠️ No hay datos para insertar en este chunk {chunk_num}")
                    offset += request.chunk_size
                    continue
                
                logger.info(f"💾 Preparados {len(datos_para_insertar)} registros para insertar")
                
                # Insertar datos en BD destino usando SQLAlchemy
                try:
                    with engine_destino.begin() as conn_dest:
                        # Estrategia según modo de exportación
                        if modo_exportacion_normalizado in ["crear", "reemplazar"]:
                            # INSERT simple (tabla nueva o vaciada)
                            logger.info(f"🔧 Ejecutando INSERT masivo de {len(datos_para_insertar)} registros...")
                            conn_dest.execute(tabla_destino_obj.insert(), datos_para_insertar)
                            logger.info(f"✅ Chunk {chunk_num} insertado: {len(datos_para_insertar)} registros (INSERT)")
                            
                        elif modo_exportacion_normalizado == "append":
                            # UPSERT manual: verificar si existe cada registro por ID
                            registros_insertados = 0
                            registros_actualizados = 0
                            
                            for fila_dict in datos_para_insertar:
                                # Verificar si existe registro con mismo ID (si viene en los datos)
                                id_origen = None
                                for col_name in fila_dict.keys():
                                    if col_name.lower() == 'id':
                                        id_origen = fila_dict[col_name]
                                        break
                                
                                if id_origen:
                                    # Verificar si existe en destino
                                    check_query = text(f"""
                                        SELECT COUNT(*) 
                                        FROM [{request.esquema_destino}].[{nombre_tabla_destino}]
                                        WHERE id = :id_val
                                    """)
                                    existe = conn_dest.execute(check_query, {"id_val": id_origen}).scalar() > 0
                                    
                                    if existe:
                                        # UPDATE
                                        set_clauses = ", ".join([f"[{col}] = :{col}" for col in fila_dict.keys()])
                                        update_query = text(f"""
                                            UPDATE [{request.esquema_destino}].[{nombre_tabla_destino}]
                                            SET {set_clauses}
                                            WHERE id = :id_val
                                        """)
                                        params = {**fila_dict, "id_val": id_origen}
                                        conn_dest.execute(update_query, params)
                                        registros_actualizados += 1
                                    else:
                                        # INSERT
                                        conn_dest.execute(tabla_destino_obj.insert(), [fila_dict])
                                        registros_insertados += 1
                                else:
                                    # Sin ID, hacer INSERT simple
                                    conn_dest.execute(tabla_destino_obj.insert(), [fila_dict])
                                    registros_insertados += 1
                            
                            logger.info(f"📦 Chunk procesado: {registros_insertados} INSERT, {registros_actualizados} UPDATE")
                        
                except Exception as e:
                    logger.error(f"❌ Error al insertar chunk: {str(e)}")
                    raise Exception(f"Error en inserción de datos: {str(e)}")
                
                registros_exportados += len(filas)
                offset += request.chunk_size
                
                logger.info(f"📦 Chunk exportado: {len(filas)} registros (Total: {registros_exportados}/{total_registros})")
        
        logger.info(f"✅ Exportación de datos completada")
        
        # 11. Obtener muestra de datos exportados (primeros 10 registros)
        muestra_datos = []
        columnas_muestra = []
        try:
            with engine_destino.connect() as conn_dest:
                muestra_query = text(f"""
                    SELECT TOP 10 * 
                    FROM [{request.esquema_destino}].[{nombre_tabla_destino}]
                    ORDER BY id
                """)
                resultado_muestra = conn_dest.execute(muestra_query)
                filas_muestra = resultado_muestra.fetchall()
                
                if filas_muestra:
                    # Obtener nombres de columnas
                    columnas_muestra = list(filas_muestra[0]._mapping.keys())
                    
                    # Convertir filas a diccionarios
                    for fila in filas_muestra:
                        fila_dict = {}
                        for col in columnas_muestra:
                            valor = fila._mapping[col]
                            # Convertir tipos no serializables a string
                            if isinstance(valor, (datetime, date)):
                                valor = valor.isoformat()
                            elif valor is None:
                                valor = None
                            else:
                                valor = str(valor) if not isinstance(valor, (int, float, bool, str)) else valor
                            fila_dict[col] = valor
                        muestra_datos.append(fila_dict)
                    
                    logger.info(f"📊 Muestra obtenida: {len(muestra_datos)} registros de {len(columnas_muestra)} columnas")
        except Exception as e:
            logger.warning(f"⚠️ No se pudo obtener muestra de datos: {str(e)}")
            muestra_datos = []
            columnas_muestra = []
        
        # 12. Crear registro de exportación (al final para evitar error NVARCHAR)
        tiempo_total = time.time() - inicio
        
        from db.models.config.migraciones import ExportacionBD
        
        try:
            exportacion = ExportacionBD(
                tabla_origen_local=request.tabla_origen_local,
                tabla_destino=nombre_tabla_destino,
                tipo_motor_destino=request.tipo_motor_destino,
                host_destino=request.host_destino,
                puerto_destino=request.puerto_destino,
                nombre_bd_destino=request.nombre_bd_destino,
                esquema_destino=request.esquema_destino,
                modo_exportacion=modo_exportacion_normalizado,
                total_registros_exportados=registros_exportados,
                total_columnas=total_columnas,
                chunk_size=request.chunk_size,
                estado="completado",
                usuario_id=current_user.codigo,
                tiempo_procesamiento_segundos=round(tiempo_total, 2)
            )
            
            db.add(exportacion)
            db.commit()
            db.refresh(exportacion)
            
            logger.info(f"✅ Registro de auditoría creado: ID {exportacion.id}")
        except Exception as e:
            logger.warning(f"⚠️ No se pudo crear registro de auditoría: {str(e)}")
            # No fallar la exportación si no se puede crear el registro
            exportacion = None
        
        logger.info(f"✅ Exportación completada: {registros_exportados} registros en {tiempo_total:.2f}s")
        
        return {
            "exito": True,
            "mensaje": "Exportación completada exitosamente",
            "exportacion_id": exportacion.id if exportacion else None,
            "tabla_origen": request.tabla_origen_local,
            "tabla_destino": f"{request.esquema_destino}.{nombre_tabla_destino}",
            "bd_destino": request.nombre_bd_destino,
            "registros_exportados": registros_exportados,
            "modo_exportacion": modo_exportacion_normalizado,
            "tiempo_total_segundos": round(tiempo_total, 2),
            "velocidad_reg_por_seg": round(registros_exportados / tiempo_total, 2) if tiempo_total > 0 else 0,
            "muestra_datos": {
                "columnas": columnas_muestra,
                "registros": muestra_datos,
                "total_mostrados": len(muestra_datos)
            }
        }
        
    except Exception as e:
        import traceback
        logger.error(f"❌ Error en exportar_tabla: {str(e)}")
        logger.error(f"Tipo de error: {type(e).__name__}")
        logger.error(f"Traceback completo:")
        logger.error(traceback.format_exc())
        
        # Intentar crear registro de error (si no existe ya)
        try:
            from db.models.config.migraciones import ExportacionBD
            exportacion_error = ExportacionBD(
                tabla_origen_local=request.tabla_origen_local,
                tabla_destino=request.tabla_destino or request.tabla_origen_local,
                tipo_motor_destino=request.tipo_motor_destino,
                host_destino=request.host_destino,
                puerto_destino=request.puerto_destino,
                nombre_bd_destino=request.nombre_bd_destino,
                esquema_destino=request.esquema_destino,
                modo_exportacion=request.modo_exportacion,
                total_columnas=0,
                chunk_size=request.chunk_size,
                estado="error",
                usuario_id=current_user.codigo,
                tiempo_procesamiento_segundos=round(time.time() - inicio, 2),
                mensaje_error=str(e)[:500]  # Limitar a 500 caracteres
            )
            db.add(exportacion_error)
            db.commit()
        except Exception as audit_error:
            logger.warning(f"⚠️ No se pudo crear registro de error: {str(audit_error)}")
        
        raise HTTPException(
            status_code=500,
            detail=f"Error al exportar tabla: {str(e)}"
        )


@router.get("/tablas-locales", summary="Listar Tablas Locales")
async def listar_tablas_locales(
    current_user: UserDB = Depends(require_role_api(["admin", "usuario"]))
):
    """
    📋 Lista todas las tablas disponibles en la BD local
    
    Útil para PASO 3 para seleccionar qué tabla exportar
    
    Returns:
        - exito: bool
        - tablas: List con nombre y cantidad de registros
        - total_tablas: int
    """
    try:
        from db.database import engine
        from sqlalchemy import text
        
        # Usar SQL directo para obtener tablas y evitar el error de NVARCHAR(max)
        query = text("""
            SELECT TABLE_NAME 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_SCHEMA = 'dbo' 
            AND TABLE_TYPE = 'BASE TABLE'
            ORDER BY TABLE_NAME
        """)
        with engine.connect() as conn:
            result = conn.execute(query)
            tablas_nombres = [row[0] for row in result.fetchall()]
        
        # Filtrar tablas del sistema
        tablas_sistema = [
            'alembic_version', 'usuarios', 'roles', 'usuario_roles',
            'migraciones_metadata', 'archivos_cargados', 'conexiones_externas',
            'migraciones_log', 'campos_mapeados', 'exportaciones_bd',
            'blog_posts', 'activity_log'
        ]
        
        tablas_usuario = [t for t in tablas_nombres if t not in tablas_sistema]
        
        # Obtener conteo de registros para cada tabla
        tablas_info = []
        with engine.connect() as conn:
            for tabla in tablas_usuario:
                try:
                    resultado = conn.execute(text(f"SELECT COUNT(*) FROM {tabla}"))
                    total_registros = resultado.scalar()
                    
                    tablas_info.append({
                        "nombre": tabla,
                        "total_registros": total_registros
                    })
                except Exception as e:
                    logger.warning(f"No se pudo contar registros de '{tabla}': {e}")
                    continue
        
        logger.info(f"📋 Tablas locales encontradas: {len(tablas_info)}")
        
        return {
            "exito": True,
            "tablas": tablas_info,
            "total_tablas": len(tablas_info)
        }
        
    except Exception as e:
        logger.error(f"❌ Error en listar_tablas_locales: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al listar tablas locales: {str(e)}"
        )


@router.get("/motores", summary="Listar Motores Soportados")
async def listar_motores():
    """
    🔧 Lista todos los motores de BD soportados con su disponibilidad.
    
    Returns:
        - motores: List con información de cada motor
        - total_disponibles: Cantidad de motores instalados
    """
    motores_info = []
    
    for motor in DatabaseConnectorFactory.get_supported_motors():
        disponible, mensaje = DatabaseConnectorFactory.is_motor_available(motor)
        
        # Información adicional
        puerto_default = {
            'mssql': 1433,
            'sqlserver': 1433,
            'postgresql': 5432,
            'postgres': 5432,
            'mysql': 3306,
            'oracle': 1521,
            'plsql': 1521
        }.get(motor, 0)
        
        motores_info.append({
            'motor': motor,
            'disponible': disponible,
            'mensaje': mensaje,
            'puerto_default': puerto_default
        })
    
    # Eliminar duplicados (mssql=sqlserver, postgresql=postgres, oracle=plsql)
    motores_unicos = {}
    for m in motores_info:
        key = m['motor'].replace('sqlserver', 'mssql').replace('postgres', 'postgresql').replace('plsql', 'oracle')
        if key not in motores_unicos or m['disponible']:
            motores_unicos[key] = m
    
    motores_list = list(motores_unicos.values())
    disponibles = [m for m in motores_list if m['disponible']]
    
    return {
        "exito": True,
        "motores": motores_list,
        "total_motores": len(motores_list),
        "total_disponibles": len(disponibles)
    }


@router.get("/health", summary="Health Check")
async def health_check():
    """
    🏥 Verifica que el router esté funcionando.
    """
    # Obtener motores disponibles
    motores_disponibles = []
    for motor in ['mssql', 'postgresql', 'mysql', 'oracle']:
        disponible, _ = DatabaseConnectorFactory.is_motor_available(motor)
        if disponible:
            motores_disponibles.append(motor)
    
    return {
        "status": "healthy",
        "service": "Migración BD Multi-Motor",
        "version": "2.0.0",
        "motores_soportados": ['mssql', 'postgresql', 'mysql', 'oracle'],
        "motores_disponibles": motores_disponibles,
        "endpoints_disponibles": [
            "/motores",
            "/test-conexion",
            "/listar-tablas",
            "/tabla-info",
            "/tabla-preview",
            "/importar",
            "/exportar",
            "/tablas-locales",
            "/health"
        ]
    }

