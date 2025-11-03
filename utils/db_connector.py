"""
Conectores Multi-Motor para Bases de Datos
===========================================

Sistema de conectores para múltiples motores de bases de datos:
- Microsoft SQL Server (MSSQL)
- PostgreSQL
- MySQL
- Oracle (PL/SQL)

Arquitectura basada en patrón Factory y clases abstractas.

Autor: Sistema SQL App
Fecha: 18 de octubre de 2025
Versión: 2.0 (Multi-Motor)
"""

from abc import ABC, abstractmethod
import pandas as pd
from typing import List, Dict, Any, Tuple, Optional, Generator
import logging

# Imports específicos por motor (con manejo de dependencias opcionales)
try:
    import pyodbc
    MSSQL_AVAILABLE = True
except ImportError:
    MSSQL_AVAILABLE = False

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    POSTGRESQL_AVAILABLE = True
except ImportError:
    POSTGRESQL_AVAILABLE = False

try:
    import mysql.connector
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False

try:
    import cx_Oracle
    ORACLE_AVAILABLE = True
except ImportError:
    ORACLE_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================
# CLASE BASE ABSTRACTA
# ============================================

class DatabaseConnector(ABC):
    """
    Clase base abstracta para conectores de bases de datos.
    
    Define la interfaz común que deben implementar todos los conectores.
    """
    
    def __init__(self, host: str, port: int, user: str, password: str, database: str):
        """
        Inicializa el conector.
        
        Args:
            host: IP o hostname del servidor
            port: Puerto de conexión
            user: Usuario de la BD
            password: Contraseña
            database: Nombre de la base de datos
        """
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.motor = self.__class__.__name__.replace('Connector', '').upper()
    
    @abstractmethod
    def test_connection(self) -> Tuple[bool, str]:
        """Prueba la conexión a la BD."""
        pass
    
    @abstractmethod
    def list_tables(self, include_row_count: bool = True) -> List[Dict[str, Any]]:
        """Lista todas las tablas de la base de datos."""
        pass
    
    @abstractmethod
    def get_table_info(self, table: str, schema: Optional[str] = None) -> Dict[str, Any]:
        """Obtiene información detallada de una tabla."""
        pass
    
    @abstractmethod
    def get_table_preview(self, table: str, schema: Optional[str] = None, limit: int = 100) -> pd.DataFrame:
        """Obtiene preview de una tabla (primeras N filas)."""
        pass
    
    @abstractmethod
    def extract_table_complete(self, table: str, schema: Optional[str] = None, chunk_size: int = 10000) -> Generator[pd.DataFrame, None, None]:
        """Extrae tabla completa en chunks."""
        pass
    
    @abstractmethod
    def get_column_types(self, table: str, schema: Optional[str] = None) -> Dict[str, str]:
        """Obtiene tipos de datos de las columnas."""
        pass
    
    @abstractmethod
    def create_table_ddl(self, table: str, columns: Dict[str, str], schema: Optional[str] = None) -> str:
        """Genera DDL para crear tabla según el motor."""
        pass
    
    @abstractmethod
    def get_sqlalchemy_url(self) -> str:
        """Genera URL de conexión para SQLAlchemy."""
        pass


# ============================================
# SQL SERVER CONNECTOR
# ============================================

class SQLServerConnector(DatabaseConnector):
    """
    Conector para Microsoft SQL Server.
    
    Permite:
    - Probar conexión
    - Listar tablas
    - Obtener preview de datos
    - Extraer tabla completa
    """
    
    def __init__(self, host: str, port: int, user: str, password: str, database: str):
        """Inicializa el conector SQL Server."""
        if not MSSQL_AVAILABLE:
            raise ImportError("pyodbc no está instalado. Ejecuta: pip install pyodbc")
        
        super().__init__(host, port, user, password, database)
        
        # Connection string
        self.connection_string = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={host},{port};"
            f"DATABASE={database};"
            f"UID={user};"
            f"PWD={password};"
            f"TrustServerCertificate=yes;"
        )
    
    def test_connection(self) -> Tuple[bool, str]:
        """
        Prueba la conexión a SQL Server.
        
        Returns:
            Tuple[bool, str]: (éxito, mensaje descriptivo)
        """
        try:
            logger.info(f"🔌 Probando conexión a {self.host}:{self.port}/{self.database}")
            conn = pyodbc.connect(self.connection_string, timeout=10)
            cursor = conn.cursor()
            
            # Obtener versión de SQL Server
            cursor.execute("SELECT @@VERSION")
            version = cursor.fetchone()[0]
            version_short = version.split('\n')[0][:100]
            
            # Contar tablas
            cursor.execute("""
                SELECT COUNT(*) 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_TYPE = 'BASE TABLE'
            """)
            tabla_count = cursor.fetchone()[0]
            
            conn.close()
            
            mensaje = f"✅ Conexión exitosa. {version_short}. Tablas disponibles: {tabla_count}"
            logger.info(mensaje)
            return True, mensaje
            
        except pyodbc.Error as e:
            mensaje = f"❌ Error de conexión: {str(e)}"
            logger.error(mensaje)
            return False, mensaje
        except Exception as e:
            mensaje = f"❌ Error inesperado: {str(e)}"
            logger.error(mensaje)
            return False, mensaje
    
    def list_tables(self, include_row_count: bool = True) -> List[Dict[str, Any]]:
        """
        Lista todas las tablas de la base de datos.
        
        Args:
            include_row_count: Si incluir conteo de filas (más lento)
        
        Returns:
            Lista de diccionarios con información de tablas
        """
        try:
            logger.info(f"📋 Listando tablas de {self.database}")
            conn = pyodbc.connect(self.connection_string, timeout=10)
            cursor = conn.cursor()
            
            if include_row_count:
                # Query con conteo de filas (puede ser lento en BDs grandes)
                query = """
                SELECT 
                    t.TABLE_SCHEMA,
                    t.TABLE_NAME,
                    ISNULL(p.rows, 0) as ROW_COUNT
                FROM INFORMATION_SCHEMA.TABLES t
                LEFT JOIN (
                    SELECT 
                        OBJECT_SCHEMA_NAME(object_id) as SCHEMA_NAME,
                        OBJECT_NAME(object_id) as TABLE_NAME,
                        SUM(rows) as rows
                    FROM sys.partitions
                    WHERE index_id IN (0, 1)
                    GROUP BY object_id
                ) p ON t.TABLE_SCHEMA = p.SCHEMA_NAME AND t.TABLE_NAME = p.TABLE_NAME
                WHERE t.TABLE_TYPE = 'BASE TABLE'
                ORDER BY t.TABLE_SCHEMA, t.TABLE_NAME
                """
            else:
                # Query simple sin conteo
                query = """
                SELECT 
                    TABLE_SCHEMA,
                    TABLE_NAME,
                    0 as ROW_COUNT
                FROM INFORMATION_SCHEMA.TABLES
                WHERE TABLE_TYPE = 'BASE TABLE'
                ORDER BY TABLE_SCHEMA, TABLE_NAME
                """
            
            cursor.execute(query)
            tables = []
            
            for row in cursor.fetchall():
                tables.append({
                    'esquema': row[0],
                    'nombre': row[1],
                    'nombre_completo': f"{row[0]}.{row[1]}",
                    'filas_estimadas': row[2] if include_row_count else None
                })
            
            conn.close()
            
            logger.info(f"✅ {len(tables)} tablas encontradas")
            return tables
            
        except Exception as e:
            logger.error(f"❌ Error al listar tablas: {str(e)}")
            raise
    
    def get_table_info(self, table: str, schema: str = 'dbo') -> Dict[str, Any]:
        """
        Obtiene información detallada de una tabla.
        
        Args:
            table: Nombre de la tabla
            schema: Esquema (por defecto 'dbo')
        
        Returns:
            Diccionario con información de la tabla
        """
        try:
            logger.info(f"ℹ️ Obteniendo info de {schema}.{table}")
            conn = pyodbc.connect(self.connection_string, timeout=10)
            cursor = conn.cursor()
            
            # Información de columnas
            query_columns = f"""
            SELECT 
                COLUMN_NAME,
                DATA_TYPE,
                CHARACTER_MAXIMUM_LENGTH,
                IS_NULLABLE
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = '{schema}' AND TABLE_NAME = '{table}'
            ORDER BY ORDINAL_POSITION
            """
            
            cursor.execute(query_columns)
            columnas = []
            
            for row in cursor.fetchall():
                col_info = {
                    'nombre': row[0],
                    'tipo': row[1],
                    'longitud': row[2],
                    'nullable': row[3] == 'YES'
                }
                columnas.append(col_info)
            
            # Conteo de filas
            cursor.execute(f"SELECT COUNT(*) FROM [{schema}].[{table}]")
            total_filas = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'esquema': schema,
                'tabla': table,
                'columnas': columnas,
                'total_filas': total_filas
            }
            
        except Exception as e:
            logger.error(f"❌ Error al obtener info de tabla: {str(e)}")
            raise
    
    def get_table_preview(self, table: str, schema: str = 'dbo', limit: int = 100) -> pd.DataFrame:
        """
        Obtiene preview de una tabla (primeras N filas).
        
        Args:
            table: Nombre de la tabla
            schema: Esquema (por defecto 'dbo')
            limit: Cantidad de filas (por defecto 100)
        
        Returns:
            DataFrame de pandas con los datos
        """
        try:
            logger.info(f"👁️ Obteniendo preview de {schema}.{table} (limit={limit})")
            conn = pyodbc.connect(self.connection_string, timeout=10)
            
            query = f"SELECT TOP {limit} * FROM [{schema}].[{table}]"
            df = pd.read_sql(query, conn)
            
            conn.close()
            
            logger.info(f"✅ Preview obtenido: {len(df)} filas, {len(df.columns)} columnas")
            return df
            
        except Exception as e:
            logger.error(f"❌ Error al obtener preview: {str(e)}")
            raise
    
    def extract_table_complete(self, table: str, schema: str = 'dbo', chunk_size: int = 10000):
        """
        Extrae tabla completa en chunks (para tablas grandes).
        
        Args:
            table: Nombre de la tabla
            schema: Esquema
            chunk_size: Tamaño de cada chunk
        
        Yields:
            DataFrames con chunks de datos
        """
        try:
            logger.info(f"📥 Extrayendo tabla completa {schema}.{table} (chunk_size={chunk_size})")
            
            # Usar SQLAlchemy engine para evitar warnings de pandas
            from sqlalchemy import create_engine
            
            # Crear connection string para SQLAlchemy
            engine_url = f"mssql+pyodbc://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}?driver=ODBC+Driver+17+for+SQL+Server"
            engine = create_engine(engine_url, pool_pre_ping=True)
            
            query = f"SELECT * FROM [{schema}].[{table}]"
            
            # Leer en chunks usando engine de SQLAlchemy
            chunk_count = 0
            for chunk in pd.read_sql(query, engine, chunksize=chunk_size):
                chunk_count += 1
                logger.info(f"  📦 Chunk #{chunk_count}: {len(chunk)} filas extraídas")
                yield chunk
            
            engine.dispose()
            logger.info(f"✅ Extracción completa de {schema}.{table} finalizada ({chunk_count} chunks)")
            
        except Exception as e:
            logger.error(f"❌ Error al extraer tabla: {str(e)}")
            raise
    
    def get_column_types(self, table: str, schema: str = 'dbo') -> Dict[str, str]:
        """
        Obtiene tipos de datos de las columnas.
        
        Args:
            table: Nombre de la tabla
            schema: Esquema
        
        Returns:
            Diccionario {nombre_columna: tipo_dato}
        """
        try:
            conn = pyodbc.connect(self.connection_string, timeout=10)
            cursor = conn.cursor()
            
            query = f"""
            SELECT COLUMN_NAME, DATA_TYPE
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = '{schema}' AND TABLE_NAME = '{table}'
            ORDER BY ORDINAL_POSITION
            """
            
            cursor.execute(query)
            
            tipos = {}
            for row in cursor.fetchall():
                tipos[row[0]] = row[1]
            
            conn.close()
            return tipos
            
        except Exception as e:
            logger.error(f"❌ Error al obtener tipos de columnas: {str(e)}")
            raise
    
    def create_table_ddl(self, table: str, columns: Dict[str, str], schema: Optional[str] = 'dbo') -> str:
        """
        Genera DDL para crear tabla en SQL Server.
        
        Args:
            table: Nombre de la tabla
            columns: Dict {nombre_columna: tipo_dato_sqlalchemy}
            schema: Esquema (por defecto 'dbo')
        
        Returns:
            String con DDL de CREATE TABLE
        """
        schema = schema or 'dbo'
        columns_ddl = []
        
        for col_name, col_type in columns.items():
            if col_name == 'id':
                continue  # Skip auto-generated ID
            
            # Mapeo de tipos SQLAlchemy a SQL Server
            tipo_sql = str(col_type).upper()
            if "VARCHAR" in tipo_sql or "TEXT" in tipo_sql or "STRING" in tipo_sql:
                tipo_sql = "NVARCHAR(255)"
            elif "INTEGER" in tipo_sql or "BIGINT" in tipo_sql:
                tipo_sql = "INT"
            elif "FLOAT" in tipo_sql or "NUMERIC" in tipo_sql or "DECIMAL" in tipo_sql:
                tipo_sql = "FLOAT"
            elif "DATETIME" in tipo_sql or "TIMESTAMP" in tipo_sql:
                tipo_sql = "DATETIME"
            elif "BOOLEAN" in tipo_sql or "BOOL" in tipo_sql:
                tipo_sql = "BIT"
            elif "DATE" in tipo_sql:
                tipo_sql = "DATE"
            else:
                tipo_sql = "NVARCHAR(255)"  # Default
            
            columns_ddl.append(f"[{col_name}] {tipo_sql} NULL")
        
        ddl = f"""
CREATE TABLE [{schema}].[{table}] (
    id INT IDENTITY(1,1) PRIMARY KEY,
    {', '.join(columns_ddl)}
)
"""
        return ddl.strip()
    
    def get_sqlalchemy_url(self) -> str:
        """
        Genera URL de conexión para SQLAlchemy con SQL Server.
        
        Returns:
            String con URL de SQLAlchemy (mssql+pyodbc://...)
        """
        from urllib.parse import quote_plus
        
        # Construir connection string para pyodbc
        conn_str = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={self.host},{self.port};"
            f"DATABASE={self.database};"
            f"UID={self.user};"
            f"PWD={self.password};"
            "TrustServerCertificate=yes;"
        )
        
        # URL encode del connection string
        conn_str_encoded = quote_plus(conn_str)
        
        # Construir URL de SQLAlchemy
        return f"mssql+pyodbc:///?odbc_connect={conn_str_encoded}"


# ============================================
# POSTGRESQL CONNECTOR
# ============================================

class PostgreSQLConnector(DatabaseConnector):
    """
    Conector para PostgreSQL.
    """
    
    def __init__(self, host: str, port: int, user: str, password: str, database: str):
        """Inicializa el conector PostgreSQL."""
        if not POSTGRESQL_AVAILABLE:
            raise ImportError("psycopg2 no está instalado. Ejecuta: pip install psycopg2-binary")
        
        super().__init__(host, port, user, password, database)
    
    def _get_connection(self):
        """Obtiene una conexión a PostgreSQL."""
        return psycopg2.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=self.database,
            connect_timeout=10
        )
    
    def test_connection(self) -> Tuple[bool, str]:
        """Prueba la conexión a PostgreSQL."""
        try:
            logger.info(f"🔌 Probando conexión a PostgreSQL {self.host}:{self.port}/{self.database}")
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Obtener versión
            cursor.execute("SELECT version()")
            version = cursor.fetchone()[0]
            version_short = version.split(',')[0][:80]
            
            # Contar tablas
            cursor.execute("""
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
                AND table_type = 'BASE TABLE'
            """)
            tabla_count = cursor.fetchone()[0]
            
            conn.close()
            
            mensaje = f"✅ Conexión exitosa. {version_short}. Tablas: {tabla_count}"
            logger.info(mensaje)
            return True, mensaje
            
        except Exception as e:
            mensaje = f"❌ Error de conexión PostgreSQL: {str(e)}"
            logger.error(mensaje)
            return False, mensaje
    
    def list_tables(self, include_row_count: bool = True) -> List[Dict[str, Any]]:
        """Lista todas las tablas de PostgreSQL."""
        try:
            logger.info(f"📋 Listando tablas de PostgreSQL {self.database}")
            conn = self._get_connection()
            cursor = conn.cursor()
            
            if include_row_count:
                query = """
                SELECT 
                    schemaname as schema_name,
                    tablename as table_name,
                    n_live_tup as row_count
                FROM pg_stat_user_tables
                ORDER BY schemaname, tablename
                """
            else:
                query = """
                SELECT 
                    table_schema as schema_name,
                    table_name,
                    0 as row_count
                FROM information_schema.tables
                WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
                AND table_type = 'BASE TABLE'
                ORDER BY table_schema, table_name
                """
            
            cursor.execute(query)
            tables = []
            
            for row in cursor.fetchall():
                tables.append({
                    'esquema': row[0],
                    'nombre': row[1],
                    'nombre_completo': f"{row[0]}.{row[1]}",
                    'filas_estimadas': row[2] if include_row_count else None
                })
            
            conn.close()
            logger.info(f"✅ {len(tables)} tablas encontradas")
            return tables
            
        except Exception as e:
            logger.error(f"❌ Error al listar tablas: {str(e)}")
            raise
    
    def get_table_info(self, table: str, schema: Optional[str] = 'public') -> Dict[str, Any]:
        """Obtiene información detallada de una tabla."""
        try:
            schema = schema or 'public'
            logger.info(f"ℹ️ Obteniendo info de {schema}.{table}")
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Información de columnas
            query_columns = f"""
            SELECT 
                column_name,
                data_type,
                character_maximum_length,
                is_nullable
            FROM information_schema.columns
            WHERE table_schema = '{schema}' AND table_name = '{table}'
            ORDER BY ordinal_position
            """
            
            cursor.execute(query_columns)
            columnas = []
            
            for row in cursor.fetchall():
                columnas.append({
                    'nombre': row[0],
                    'tipo': row[1],
                    'longitud': row[2],
                    'nullable': row[3] == 'YES'
                })
            
            # Conteo de filas
            cursor.execute(f'SELECT COUNT(*) FROM "{schema}"."{table}"')
            total_filas = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'esquema': schema,
                'tabla': table,
                'columnas': columnas,
                'total_filas': total_filas
            }
            
        except Exception as e:
            logger.error(f"❌ Error al obtener info: {str(e)}")
            raise
    
    def get_table_preview(self, table: str, schema: Optional[str] = 'public', limit: int = 100) -> pd.DataFrame:
        """Obtiene preview de una tabla."""
        try:
            schema = schema or 'public'
            logger.info(f"👁️ Preview de {schema}.{table} (limit={limit})")
            conn = self._get_connection()
            
            query = f'SELECT * FROM "{schema}"."{table}" LIMIT {limit}'
            df = pd.read_sql(query, conn)
            
            conn.close()
            logger.info(f"✅ Preview: {len(df)} filas, {len(df.columns)} columnas")
            return df
            
        except Exception as e:
            logger.error(f"❌ Error preview: {str(e)}")
            raise
    
    def extract_table_complete(self, table: str, schema: Optional[str] = 'public', chunk_size: int = 10000) -> Generator[pd.DataFrame, None, None]:
        """Extrae tabla completa en chunks."""
        try:
            schema = schema or 'public'
            logger.info(f"📥 Extrayendo {schema}.{table}")
            conn = self._get_connection()
            
            query = f'SELECT * FROM "{schema}"."{table}"'
            
            for chunk in pd.read_sql(query, conn, chunksize=chunk_size):
                logger.info(f"  Chunk de {len(chunk)} filas")
                yield chunk
            
            conn.close()
            logger.info(f"✅ Extracción completa")
            
        except Exception as e:
            logger.error(f"❌ Error extracción: {str(e)}")
            raise
    
    def get_column_types(self, table: str, schema: Optional[str] = 'public') -> Dict[str, str]:
        """Obtiene tipos de columnas."""
        try:
            schema = schema or 'public'
            conn = self._get_connection()
            cursor = conn.cursor()
            
            query = f"""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_schema = '{schema}' AND table_name = '{table}'
            ORDER BY ordinal_position
            """
            
            cursor.execute(query)
            tipos = {row[0]: row[1] for row in cursor.fetchall()}
            
            conn.close()
            return tipos
            
        except Exception as e:
            logger.error(f"❌ Error tipos: {str(e)}")
            raise
    
    def create_table_ddl(self, table: str, columns: Dict[str, str], schema: Optional[str] = 'public') -> str:
        """Genera DDL para PostgreSQL."""
        schema = schema or 'public'
        columns_ddl = []
        
        for col_name, col_type in columns.items():
            if col_name == 'id':
                continue
            
            tipo_sql = str(col_type).upper()
            if "VARCHAR" in tipo_sql or "TEXT" in tipo_sql or "STRING" in tipo_sql:
                tipo_sql = "VARCHAR(255)"
            elif "INTEGER" in tipo_sql or "BIGINT" in tipo_sql:
                tipo_sql = "INTEGER"
            elif "FLOAT" in tipo_sql or "NUMERIC" in tipo_sql or "DECIMAL" in tipo_sql:
                tipo_sql = "NUMERIC"
            elif "DATETIME" in tipo_sql or "TIMESTAMP" in tipo_sql:
                tipo_sql = "TIMESTAMP"
            elif "BOOLEAN" in tipo_sql or "BOOL" in tipo_sql:
                tipo_sql = "BOOLEAN"
            elif "DATE" in tipo_sql:
                tipo_sql = "DATE"
            else:
                tipo_sql = "VARCHAR(255)"
            
            columns_ddl.append(f'"{col_name}" {tipo_sql}')
        
        ddl = f"""
CREATE TABLE "{schema}"."{table}" (
    id SERIAL PRIMARY KEY,
    {', '.join(columns_ddl)}
)
"""
        return ddl.strip()
    
    def get_sqlalchemy_url(self) -> str:
        """
        Genera URL de conexión para SQLAlchemy con PostgreSQL.
        
        Returns:
            String con URL de SQLAlchemy (postgresql://...)
        """
        from urllib.parse import quote_plus
        
        # URL encode de password por si tiene caracteres especiales
        password_encoded = quote_plus(self.password)
        
        # Construir URL de SQLAlchemy
        return f"postgresql://{self.user}:{password_encoded}@{self.host}:{self.port}/{self.database}"


# ============================================
# MYSQL CONNECTOR
# ============================================

class MySQLConnector(DatabaseConnector):
    """
    Conector para MySQL/MariaDB.
    """
    
    def __init__(self, host: str, port: int, user: str, password: str, database: str):
        """Inicializa el conector MySQL."""
        if not MYSQL_AVAILABLE:
            raise ImportError("mysql-connector-python no está instalado. Ejecuta: pip install mysql-connector-python")
        
        super().__init__(host, port, user, password, database)
    
    def _get_connection(self):
        """Obtiene una conexión a MySQL."""
        return mysql.connector.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=self.database,
            connect_timeout=10
        )
    
    def test_connection(self) -> Tuple[bool, str]:
        """Prueba la conexión a MySQL."""
        try:
            logger.info(f"🔌 Probando conexión a MySQL {self.host}:{self.port}/{self.database}")
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Versión
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()[0]
            
            # Contar tablas
            cursor.execute(f"SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = '{self.database}'")
            tabla_count = cursor.fetchone()[0]
            
            conn.close()
            
            mensaje = f"✅ Conexión exitosa. MySQL {version}. Tablas: {tabla_count}"
            logger.info(mensaje)
            return True, mensaje
            
        except Exception as e:
            mensaje = f"❌ Error de conexión MySQL: {str(e)}"
            logger.error(mensaje)
            return False, mensaje
    
    def list_tables(self, include_row_count: bool = True) -> List[Dict[str, Any]]:
        """Lista todas las tablas de MySQL."""
        try:
            logger.info(f"📋 Listando tablas de MySQL {self.database}")
            conn = self._get_connection()
            cursor = conn.cursor()
            
            if include_row_count:
                query = f"""
                SELECT 
                    table_schema,
                    table_name,
                    table_rows
                FROM information_schema.tables
                WHERE table_schema = '{self.database}'
                AND table_type = 'BASE TABLE'
                ORDER BY table_name
                """
            else:
                query = f"""
                SELECT 
                    table_schema,
                    table_name,
                    0 as table_rows
                FROM information_schema.tables
                WHERE table_schema = '{self.database}'
                AND table_type = 'BASE TABLE'
                ORDER BY table_name
                """
            
            cursor.execute(query)
            tables = []
            
            for row in cursor.fetchall():
                tables.append({
                    'esquema': row[0],
                    'nombre': row[1],
                    'nombre_completo': f"{row[0]}.{row[1]}",
                    'filas_estimadas': row[2] if include_row_count else None
                })
            
            conn.close()
            logger.info(f"✅ {len(tables)} tablas encontradas")
            return tables
            
        except Exception as e:
            logger.error(f"❌ Error al listar tablas: {str(e)}")
            raise
    
    def get_table_info(self, table: str, schema: Optional[str] = None) -> Dict[str, Any]:
        """Obtiene información detallada de una tabla."""
        try:
            schema = schema or self.database
            logger.info(f"ℹ️ Obteniendo info de {schema}.{table}")
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Información de columnas
            query_columns = f"""
            SELECT 
                column_name,
                data_type,
                character_maximum_length,
                is_nullable
            FROM information_schema.columns
            WHERE table_schema = '{schema}' AND table_name = '{table}'
            ORDER BY ordinal_position
            """
            
            cursor.execute(query_columns)
            columnas = []
            
            for row in cursor.fetchall():
                columnas.append({
                    'nombre': row[0],
                    'tipo': row[1],
                    'longitud': row[2],
                    'nullable': row[3] == 'YES'
                })
            
            # Conteo de filas
            cursor.execute(f"SELECT COUNT(*) FROM `{schema}`.`{table}`")
            total_filas = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'esquema': schema,
                'tabla': table,
                'columnas': columnas,
                'total_filas': total_filas
            }
            
        except Exception as e:
            logger.error(f"❌ Error al obtener info: {str(e)}")
            raise
    
    def get_table_preview(self, table: str, schema: Optional[str] = None, limit: int = 100) -> pd.DataFrame:
        """Obtiene preview de una tabla."""
        try:
            schema = schema or self.database
            logger.info(f"👁️ Preview de {schema}.{table} (limit={limit})")
            conn = self._get_connection()
            
            query = f"SELECT * FROM `{schema}`.`{table}` LIMIT {limit}"
            df = pd.read_sql(query, conn)
            
            conn.close()
            logger.info(f"✅ Preview: {len(df)} filas, {len(df.columns)} columnas")
            return df
            
        except Exception as e:
            logger.error(f"❌ Error preview: {str(e)}")
            raise
    
    def extract_table_complete(self, table: str, schema: Optional[str] = None, chunk_size: int = 10000) -> Generator[pd.DataFrame, None, None]:
        """Extrae tabla completa en chunks."""
        try:
            schema = schema or self.database
            logger.info(f"📥 Extrayendo {schema}.{table}")
            conn = self._get_connection()
            
            query = f"SELECT * FROM `{schema}`.`{table}`"
            
            for chunk in pd.read_sql(query, conn, chunksize=chunk_size):
                logger.info(f"  Chunk de {len(chunk)} filas")
                yield chunk
            
            conn.close()
            logger.info(f"✅ Extracción completa")
            
        except Exception as e:
            logger.error(f"❌ Error extracción: {str(e)}")
            raise
    
    def get_column_types(self, table: str, schema: Optional[str] = None) -> Dict[str, str]:
        """Obtiene tipos de columnas."""
        try:
            schema = schema or self.database
            conn = self._get_connection()
            cursor = conn.cursor()
            
            query = f"""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_schema = '{schema}' AND table_name = '{table}'
            ORDER BY ordinal_position
            """
            
            cursor.execute(query)
            tipos = {row[0]: row[1] for row in cursor.fetchall()}
            
            conn.close()
            return tipos
            
        except Exception as e:
            logger.error(f"❌ Error tipos: {str(e)}")
            raise
    
    def create_table_ddl(self, table: str, columns: Dict[str, str], schema: Optional[str] = None) -> str:
        """Genera DDL para MySQL."""
        schema = schema or self.database
        columns_ddl = []
        
        for col_name, col_type in columns.items():
            if col_name == 'id':
                continue
            
            tipo_sql = str(col_type).upper()
            if "VARCHAR" in tipo_sql or "TEXT" in tipo_sql or "STRING" in tipo_sql:
                tipo_sql = "VARCHAR(255)"
            elif "INTEGER" in tipo_sql or "BIGINT" in tipo_sql:
                tipo_sql = "INT"
            elif "FLOAT" in tipo_sql or "NUMERIC" in tipo_sql or "DECIMAL" in tipo_sql:
                tipo_sql = "FLOAT"
            elif "DATETIME" in tipo_sql or "TIMESTAMP" in tipo_sql:
                tipo_sql = "DATETIME"
            elif "BOOLEAN" in tipo_sql or "BOOL" in tipo_sql:
                tipo_sql = "TINYINT(1)"
            elif "DATE" in tipo_sql:
                tipo_sql = "DATE"
            else:
                tipo_sql = "VARCHAR(255)"
            
            columns_ddl.append(f"`{col_name}` {tipo_sql}")
        
        ddl = f"""
CREATE TABLE `{schema}`.`{table}` (
    id INT AUTO_INCREMENT PRIMARY KEY,
    {', '.join(columns_ddl)}
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
"""
        return ddl.strip()
    
    def get_sqlalchemy_url(self) -> str:
        """
        Genera URL de conexión para SQLAlchemy con MySQL.
        
        Returns:
            String con URL de SQLAlchemy (mysql+mysqlconnector://...)
        """
        from urllib.parse import quote_plus
        
        # URL encode de password
        password_encoded = quote_plus(self.password)
        
        # Construir URL de SQLAlchemy
        return f"mysql+mysqlconnector://{self.user}:{password_encoded}@{self.host}:{self.port}/{self.database}"


# ============================================
# ORACLE CONNECTOR
# ============================================

class OracleConnector(DatabaseConnector):
    """
    Conector para Oracle Database (PL/SQL).
    """
    
    def __init__(self, host: str, port: int, user: str, password: str, database: str):
        """Inicializa el conector Oracle."""
        if not ORACLE_AVAILABLE:
            raise ImportError("cx_Oracle no está instalado. Ejecuta: pip install cx_Oracle")
        
        super().__init__(host, port, user, password, database)
        self.dsn = f"{host}:{port}/{database}"
    
    def _get_connection(self):
        """Obtiene una conexión a Oracle."""
        return cx_Oracle.connect(
            user=self.user,
            password=self.password,
            dsn=self.dsn
        )
    
    def test_connection(self) -> Tuple[bool, str]:
        """Prueba la conexión a Oracle."""
        try:
            logger.info(f"🔌 Probando conexión a Oracle {self.host}:{self.port}/{self.database}")
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Versión
            cursor.execute("SELECT * FROM v$version WHERE ROWNUM = 1")
            version = cursor.fetchone()[0]
            
            # Contar tablas
            cursor.execute(f"SELECT COUNT(*) FROM all_tables WHERE owner = UPPER('{self.user}')")
            tabla_count = cursor.fetchone()[0]
            
            conn.close()
            
            mensaje = f"✅ Conexión exitosa. {version[:80]}. Tablas: {tabla_count}"
            logger.info(mensaje)
            return True, mensaje
            
        except Exception as e:
            mensaje = f"❌ Error de conexión Oracle: {str(e)}"
            logger.error(mensaje)
            return False, mensaje
    
    def list_tables(self, include_row_count: bool = True) -> List[Dict[str, Any]]:
        """Lista todas las tablas de Oracle."""
        try:
            logger.info(f"📋 Listando tablas de Oracle")
            conn = self._get_connection()
            cursor = conn.cursor()
            
            if include_row_count:
                query = f"""
                SELECT 
                    owner,
                    table_name,
                    num_rows
                FROM all_tables
                WHERE owner = UPPER('{self.user}')
                ORDER BY table_name
                """
            else:
                query = f"""
                SELECT 
                    owner,
                    table_name,
                    0 as num_rows
                FROM all_tables
                WHERE owner = UPPER('{self.user}')
                ORDER BY table_name
                """
            
            cursor.execute(query)
            tables = []
            
            for row in cursor.fetchall():
                tables.append({
                    'esquema': row[0],
                    'nombre': row[1],
                    'nombre_completo': f"{row[0]}.{row[1]}",
                    'filas_estimadas': row[2] if include_row_count else None
                })
            
            conn.close()
            logger.info(f"✅ {len(tables)} tablas encontradas")
            return tables
            
        except Exception as e:
            logger.error(f"❌ Error al listar tablas: {str(e)}")
            raise
    
    def get_table_info(self, table: str, schema: Optional[str] = None) -> Dict[str, Any]:
        """Obtiene información detallada de una tabla."""
        try:
            schema = schema or self.user.upper()
            logger.info(f"ℹ️ Obteniendo info de {schema}.{table}")
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Información de columnas
            query_columns = f"""
            SELECT 
                column_name,
                data_type,
                data_length,
                nullable
            FROM all_tab_columns
            WHERE owner = UPPER('{schema}') AND table_name = UPPER('{table}')
            ORDER BY column_id
            """
            
            cursor.execute(query_columns)
            columnas = []
            
            for row in cursor.fetchall():
                columnas.append({
                    'nombre': row[0],
                    'tipo': row[1],
                    'longitud': row[2],
                    'nullable': row[3] == 'Y'
                })
            
            # Conteo de filas
            cursor.execute(f'SELECT COUNT(*) FROM "{schema}"."{table}"')
            total_filas = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'esquema': schema,
                'tabla': table,
                'columnas': columnas,
                'total_filas': total_filas
            }
            
        except Exception as e:
            logger.error(f"❌ Error al obtener info: {str(e)}")
            raise
    
    def get_table_preview(self, table: str, schema: Optional[str] = None, limit: int = 100) -> pd.DataFrame:
        """Obtiene preview de una tabla."""
        try:
            schema = schema or self.user.upper()
            logger.info(f"👁️ Preview de {schema}.{table} (limit={limit})")
            conn = self._get_connection()
            
            query = f'SELECT * FROM "{schema}"."{table}" WHERE ROWNUM <= {limit}'
            df = pd.read_sql(query, conn)
            
            conn.close()
            logger.info(f"✅ Preview: {len(df)} filas, {len(df.columns)} columnas")
            return df
            
        except Exception as e:
            logger.error(f"❌ Error preview: {str(e)}")
            raise
    
    def extract_table_complete(self, table: str, schema: Optional[str] = None, chunk_size: int = 10000) -> Generator[pd.DataFrame, None, None]:
        """Extrae tabla completa en chunks."""
        try:
            schema = schema or self.user.upper()
            logger.info(f"📥 Extrayendo {schema}.{table}")
            conn = self._get_connection()
            
            query = f'SELECT * FROM "{schema}"."{table}"'
            
            for chunk in pd.read_sql(query, conn, chunksize=chunk_size):
                logger.info(f"  Chunk de {len(chunk)} filas")
                yield chunk
            
            conn.close()
            logger.info(f"✅ Extracción completa")
            
        except Exception as e:
            logger.error(f"❌ Error extracción: {str(e)}")
            raise
    
    def get_column_types(self, table: str, schema: Optional[str] = None) -> Dict[str, str]:
        """Obtiene tipos de columnas."""
        try:
            schema = schema or self.user.upper()
            conn = self._get_connection()
            cursor = conn.cursor()
            
            query = f"""
            SELECT column_name, data_type
            FROM all_tab_columns
            WHERE owner = UPPER('{schema}') AND table_name = UPPER('{table}')
            ORDER BY column_id
            """
            
            cursor.execute(query)
            tipos = {row[0]: row[1] for row in cursor.fetchall()}
            
            conn.close()
            return tipos
            
        except Exception as e:
            logger.error(f"❌ Error tipos: {str(e)}")
            raise
    
    def create_table_ddl(self, table: str, columns: Dict[str, str], schema: Optional[str] = None) -> str:
        """Genera DDL para Oracle."""
        schema = schema or self.user.upper()
        columns_ddl = []
        
        for col_name, col_type in columns.items():
            if col_name == 'id':
                continue
            
            tipo_sql = str(col_type).upper()
            if "VARCHAR" in tipo_sql or "TEXT" in tipo_sql or "STRING" in tipo_sql:
                tipo_sql = "VARCHAR2(255)"
            elif "INTEGER" in tipo_sql or "BIGINT" in tipo_sql:
                tipo_sql = "NUMBER(10)"
            elif "FLOAT" in tipo_sql or "NUMERIC" in tipo_sql or "DECIMAL" in tipo_sql:
                tipo_sql = "NUMBER"
            elif "DATETIME" in tipo_sql or "TIMESTAMP" in tipo_sql:
                tipo_sql = "TIMESTAMP"
            elif "BOOLEAN" in tipo_sql or "BOOL" in tipo_sql:
                tipo_sql = "NUMBER(1)"
            elif "DATE" in tipo_sql:
                tipo_sql = "DATE"
            else:
                tipo_sql = "VARCHAR2(255)"
            
            columns_ddl.append(f'"{col_name}" {tipo_sql}')
        
        ddl = f"""
CREATE TABLE "{schema}"."{table}" (
    id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    {', '.join(columns_ddl)}
)
"""
        return ddl.strip()
    
    def get_sqlalchemy_url(self) -> str:
        """
        Genera URL de conexión para SQLAlchemy con Oracle.
        
        Returns:
            String con URL de SQLAlchemy (oracle+cx_oracle://...)
        """
        from urllib.parse import quote_plus
        
        # URL encode de password
        password_encoded = quote_plus(self.password)
        
        # Construir URL de SQLAlchemy
        return f"oracle+cx_oracle://{self.user}:{password_encoded}@{self.host}:{self.port}/{self.database}"


# ============================================
# FACTORY PATTERN
# ============================================

class DatabaseConnectorFactory:
    """
    Factory para crear conectores según el tipo de motor.
    """
    
    _connectors = {
        'mssql': SQLServerConnector,
        'sqlserver': SQLServerConnector,
        'postgresql': PostgreSQLConnector,
        'postgres': PostgreSQLConnector,
        'mysql': MySQLConnector,
        'oracle': OracleConnector,
        'plsql': OracleConnector
    }
    
    @classmethod
    def create(cls, tipo_motor: str, host: str, port: int, user: str, password: str, database: str) -> DatabaseConnector:
        """
        Crea un conector según el tipo de motor.
        
        Args:
            tipo_motor: Tipo de motor (mssql, postgresql, mysql, oracle)
            host, port, user, password, database: Datos de conexión
        
        Returns:
            Instancia de DatabaseConnector específica
        
        Raises:
            ValueError: Si el motor no está soportado
        """
        motor_lower = tipo_motor.lower()
        
        if motor_lower not in cls._connectors:
            motores_disponibles = ', '.join(cls._connectors.keys())
            raise ValueError(f"Motor '{tipo_motor}' no soportado. Disponibles: {motores_disponibles}")
        
        connector_class = cls._connectors[motor_lower]
        
        try:
            return connector_class(host, port, user, password, database)
        except ImportError as e:
            raise ImportError(f"No se puede usar {tipo_motor}: {str(e)}")
    
    @classmethod
    def get_supported_motors(cls) -> List[str]:
        """Retorna lista de motores soportados."""
        return list(set(cls._connectors.keys()))
    
    @classmethod
    def is_motor_available(cls, tipo_motor: str) -> Tuple[bool, str]:
        """
        Verifica si un motor está disponible (librería instalada).
        
        Returns:
            Tuple[bool, str]: (disponible, mensaje)
        """
        motor_lower = tipo_motor.lower()
        
        if motor_lower not in cls._connectors:
            return False, f"Motor '{tipo_motor}' no reconocido"
        
        # Verificar disponibilidad de librería
        if motor_lower in ['mssql', 'sqlserver']:
            return MSSQL_AVAILABLE, "pyodbc instalado" if MSSQL_AVAILABLE else "Instalar: pip install pyodbc"
        elif motor_lower in ['postgresql', 'postgres']:
            return POSTGRESQL_AVAILABLE, "psycopg2 instalado" if POSTGRESQL_AVAILABLE else "Instalar: pip install psycopg2-binary"
        elif motor_lower == 'mysql':
            return MYSQL_AVAILABLE, "mysql-connector instalado" if MYSQL_AVAILABLE else "Instalar: pip install mysql-connector-python"
        elif motor_lower in ['oracle', 'plsql']:
            return ORACLE_AVAILABLE, "cx_Oracle instalado" if ORACLE_AVAILABLE else "Instalar: pip install cx_Oracle"
        
        return False, "Motor no reconocido"


# ============================================
# HELPER FUNCTIONS
# ============================================

def test_connection_simple(tipo_motor: str, host: str, port: int, user: str, password: str, database: str) -> Tuple[bool, str]:
    """
    Función helper para probar conexión rápidamente con cualquier motor.
    
    Args:
        tipo_motor: Tipo de motor (mssql, postgresql, mysql, oracle)
        host, port, user, password, database: Datos de conexión
    
    Returns:
        Tuple[bool, str]: (éxito, mensaje)
    """
    try:
        connector = DatabaseConnectorFactory.create(tipo_motor, host, port, user, password, database)
        return connector.test_connection()
    except Exception as e:
        return False, f"Error al crear conector: {str(e)}"


def get_connector(tipo_motor: str, host: str, port: int, user: str, password: str, database: str) -> DatabaseConnector:
    """
    Función helper para obtener un conector configurado.
    
    Args:
        tipo_motor: Tipo de motor
        host, port, user, password, database: Datos de conexión
    
    Returns:
        DatabaseConnector: Instancia del conector
    """
    return DatabaseConnectorFactory.create(tipo_motor, host, port, user, password, database)
