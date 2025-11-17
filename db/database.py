# =============================================================================
# database.py - Configuración y utilidades de base de datos para SQL_APP
# =============================================================================
# Este módulo centraliza la configuración y utilidades de acceso a la base de datos
# para la aplicación FastAPI. Incluye:
# - Carga de variables de entorno y configuración de SQLAlchemy.
# - Creación y verificación de la base de datos y tablas.
# - Compatibilidad con SQL Server (prioridad), PostgreSQL y SQLite.
# - Funciones utilitarias para migraciones y manejo de errores.
#
# Notas profesionales:
# - No contiene lógica de negocio, solo inicialización y utilidades de infraestructura.
# - Los mensajes de ayuda y advertencia son claros para facilitar el diagnóstico.
# - Se recomienda mantener este archivo libre de prints de debug en producción.
# =============================================================================

import os
import sys
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# =============================
# CONFIGURACIÓN DE CONEXIÓN Y SQLALCHEMY
# =============================
from sqlalchemy import MetaData, Table, create_engine, inspect, text
from sqlalchemy.exc import InterfaceError, NoReferencedTableError, OperationalError, ProgrammingError
from sqlalchemy.ext.declarative import DeferredReflection
from fastapi import HTTPException
from sqlalchemy.orm import declarative_base, sessionmaker
import importlib

# Variables de entorno
DB_TYPE = os.getenv("DB_TYPE", "sqlserver").split('#')[0].strip()
DB_USER = os.getenv("DB_USER", "sa")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "sqlapp")
DB_DRIVER = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")
# Nueva opción: usar pymssql en lugar de pyodbc (más simple para Azure)
USE_PYMSSQL = os.getenv("USE_PYMSSQL", "False").lower() in ('true', '1', 't', 'yes')

# DEBUG: Log de configuración de BD
print(f"🔍 DB_TYPE: {DB_TYPE}")
print(f"🔍 DB_HOST: {DB_HOST}")
print(f"🔍 DB_NAME: {DB_NAME}")
print(f"🔍 DB_USER: {DB_USER}")
print(f"🔍 USE_PYMSSQL: {USE_PYMSSQL}")
print(f"🔍 DB_DRIVER: {DB_DRIVER}")

POOL_SIZE = int(os.getenv("POOL_SIZE", "5"))
MAX_OVERFLOW = int(os.getenv("MAX_OVERFLOW", "10"))
POOL_TIMEOUT = int(os.getenv("POOL_TIMEOUT", "30"))
POOL_PRE_PING = os.getenv("POOL_PRE_PING", "True").lower() in ('true', '1', 't')
POOL_RECYCLE = int(os.getenv("POOL_RECYCLE", "3600"))

# =============================
# SECCIÓN: SQL SERVER (PRIORIDAD)
# =============================
if DB_TYPE == "sqlserver":
    try:
        if USE_PYMSSQL:
            # Usar pymssql (no requiere ODBC instalado - más simple para Azure)
            SQLALCHEMY_DATABASE_URL = f"mssql+pymssql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
            SQLALCHEMY_MASTER_URL = f"mssql+pymssql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/master"
            print("✅ Usando pymssql driver (sin dependencia de ODBC)")
            print(f"🔍 URL BD: {SQLALCHEMY_DATABASE_URL.replace(DB_PASSWORD, '***')}")
        else:
            # Usar pyodbc (requiere ODBC instalado)
            SQLALCHEMY_DATABASE_URL = f"mssql+pyodbc://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}?driver={DB_DRIVER}"
            SQLALCHEMY_MASTER_URL = f"mssql+pyodbc://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/master?driver={DB_DRIVER}"
            print(f"✅ Usando pyodbc driver: {DB_DRIVER}")
            print(f"🔍 URL BD: {SQLALCHEMY_DATABASE_URL.replace(DB_PASSWORD, '***')}")
        
        print("🔍 Creando master_engine...")
        master_engine = create_engine(SQLALCHEMY_MASTER_URL, isolation_level="AUTOCOMMIT")
        print("✅ master_engine creado exitosamente")
        
        print("🔍 Creando engine principal...")
        engine = create_engine(
            SQLALCHEMY_DATABASE_URL,
            pool_size=POOL_SIZE,
            max_overflow=MAX_OVERFLOW,
            pool_timeout=POOL_TIMEOUT,
            pool_pre_ping=POOL_PRE_PING,
            pool_recycle=POOL_RECYCLE
        )
        print("✅ Engine principal creado exitosamente")
        
    except Exception as e:
        print(f"❌ ERROR al crear engines: {e}")
        print(f"❌ Tipo de error: {type(e)}")
        raise
    
    # Validación y advertencias
    if USE_PYMSSQL and not SQLALCHEMY_DATABASE_URL.startswith("mssql+pymssql://"):
        raise ValueError(f"Error en configuración pymssql: {SQLALCHEMY_DATABASE_URL}")
    elif not USE_PYMSSQL and not SQLALCHEMY_DATABASE_URL.startswith("mssql+pyodbc://"):
        raise ValueError(
            f"SQLALCHEMY_DATABASE_URL no está configurado correctamente para SQL Server: {SQLALCHEMY_DATABASE_URL}\n"
            "Ejemplo correcto: mssql+pyodbc://usuario:clave@host/basededatos?driver=ODBC+Driver+17+for+SQL+Server"
        )
    
    if not USE_PYMSSQL and "ODBC Driver 17 for SQL Server" not in DB_DRIVER and "ODBC Driver 18 for SQL Server" not in DB_DRIVER:
        print("⚠️  ADVERTENCIA: El driver de SQL Server no es el recomendado. Usa 'ODBC Driver 17 for SQL Server' o 'ODBC Driver 18 for SQL Server'.")

# =============================
# SECCIÓN: POSTGRESQL
# =============================
elif DB_TYPE == "postgresql":
    SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}")
    master_engine = create_engine(
        os.getenv("DATABASE_URL", f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/postgres"),
        isolation_level="AUTOCOMMIT"
    )
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        pool_size=POOL_SIZE,
        max_overflow=MAX_OVERFLOW,
        pool_timeout=POOL_TIMEOUT,
        pool_pre_ping=POOL_PRE_PING,
        pool_recycle=POOL_RECYCLE
    )

# =============================
# SECCIÓN: SQLITE
# =============================
else:
    SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./sql_app/sql_app.db")
    master_engine = None
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=True, bind=engine)
Base = declarative_base()

# Dependencia de base de datos
def get_db():
    db = None
    try:
        db = SessionLocal()
        yield db
    except OperationalError as e:
        print(f"Error de conexión a la BD: {e}")
        yield None
    finally:
        if db is not None:
            db.close()

# Crear la base de datos si no existe (solo en entorno local)
def create_database():
    # Para SQLite, no necesitamos crear la base de datos manualmente
    if DB_TYPE == "sqlite":
        return
    try:
        with master_engine.connect() as connection:
            if DB_TYPE == "sqlserver":
                connection.execute(text(f"IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = '{DB_NAME}') CREATE DATABASE {DB_NAME}"))
                connection.execute(text(f"ALTER DATABASE {DB_NAME} SET RECOVERY SIMPLE"))
                connection.execute(text(f"ALTER DATABASE {DB_NAME} SET AUTO_SHRINK ON"))
            elif DB_TYPE == "postgresql":
                result = connection.execute(text(f"SELECT 1 FROM pg_database WHERE datname = '{DB_NAME}'"))
                if not result.scalar():
                    connection.execute(text(f"CREATE DATABASE {DB_NAME}"))
    except (OperationalError, InterfaceError, ProgrammingError) as e:
        msg = str(e)
        if "Error de inicio de sesión" in msg or "login failed" in msg.lower():
            print("⚠️  No se pudo conectar a la base de datos. Verifica usuario y contraseña.")
        elif "ya existe" in msg.lower() or "already exists" in msg.lower():
            pass
        else:
            print(f"⚠️  Error al crear la base de datos: {e}")

# Función para cargar el modelo Roles primero
def ensure_roles_model():
    try:
        # Intentar importar el modelo Roles existente
        try:
            importlib.import_module("db.models.roles")
        except ImportError:
            # Si no existe, crearlo
            import os
            models_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'db', 'models')
            os.makedirs(models_dir, exist_ok=True)
            
            roles_file_path = os.path.join(models_dir, 'roles.py')
            
            if not os.path.exists(roles_file_path):
                with open(roles_file_path, 'w') as f:
                    f.write("""from sqlalchemy import Column, Integer, String
from db.database import Base

class Roles(Base):
    __tablename__ = "Roles"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), unique=True)
    descripcion = Column(String(255), nullable=True)
""")
                importlib.import_module("db.models.roles")
        
        # Crear solo la tabla Roles primero
        from sqlalchemy import MetaData
        temp_metadata = MetaData()
        for table_name, table in Base.metadata.tables.items():
            if table_name == "Roles":
                table.tometadata(temp_metadata)
                try:
                    temp_metadata.create_all(bind=engine)
                except (OperationalError, InterfaceError, ProgrammingError) as e:
                    msg = str(e)
                    if "Error de inicio de sesión" in msg or "login failed" in msg.lower():
                        print("⚠️  No se pudo conectar a la base de datos. Verifica usuario y contraseña.")
                    elif "ya existe" in msg.lower() or "already exists" in msg.lower():
                        pass
                    else:
                        print(f"⚠️  Error al crear tabla Roles: {e}")
                break
                
    except Exception as e:
        print(f"Error al asegurar el modelo Roles: {e}")

# Crear las tablas en la base de datos
def create_tables():
    try:
        # Primero asegurar que exista la tabla Roles
        ensure_roles_model()
        
        # Crear todas las demás tablas usando el método estándar de SQLAlchemy
        try:
            Base.metadata.create_all(bind=engine)
        except (OperationalError, InterfaceError, ProgrammingError) as e:
            msg = str(e)
            if "Error de inicio de sesión" in msg or "login failed" in msg.lower():
                print("⚠️  No se pudo conectar a la base de datos. Verifica usuario y contraseña.")
            elif "ya existe" in msg.lower() or "already exists" in msg.lower():
                pass
            else:
                print(f"⚠️  Error al crear tablas: {e}")
    except NoReferencedTableError as e:
        print(f"Error de tabla referenciada: {e}")
        # Si falla porque falta una tabla referenciada, intenta manejar caso por caso
        if "Roles" in str(e):
            ensure_roles_model()
            try:
                Base.metadata.create_all(bind=engine)
            except Exception as e2:
                print(f"⚠️  Error al crear tablas tras asegurar Roles: {e2}")
    except Exception as e:
        print(f"⚠️  Error inesperado al crear tablas: {e}")

# Eliminar cualquier lógica residual de PostgreSQL
if 'psycopg2' in sys.modules:
    del sys.modules['psycopg2']
    print("Referencia a psycopg2 eliminada.")

# Asegurar que SQLALCHEMY_DATABASE_URL esté configurado para SQL Server
if not (SQLALCHEMY_DATABASE_URL.startswith("mssql+pyodbc://") or SQLALCHEMY_DATABASE_URL.startswith("mssql+pymssql://")):
    raise ValueError("SQLALCHEMY_DATABASE_URL no está configurado correctamente para SQL Server.")

# =============================
# AUTO-ACTUALIZAR BASE DE DATOS CON ALEMBIC EN STARTUP
# =============================
def run_alembic_upgrade():
    import subprocess
    import logging
    try:
        result = subprocess.run([
            sys.executable, '-m', 'alembic', 'upgrade', 'head'
        ], cwd=os.path.dirname(os.path.dirname(__file__)), capture_output=True, text=True)
        if result.returncode == 0:
            return True
        else:
            # Solo mostrar error si es realmente crítico
            if result.stderr.strip():
                print(f"[Alembic] Error al aplicar migraciones: {result.stderr}")
            return not result.stderr.strip()
    except Exception as e:
        print(f"[Alembic] Excepción al ejecutar migraciones: {e}")
        return False

# REMOVIDO: Ejecutar migraciones automáticamente al importar este módulo
# run_alembic_upgrade()

# La base de datos se crea pero las tablas no se crean automáticamente
# para evitar problemas de orden de creación
create_database()  # Se omitirá en Heroku
# Las tablas se crearán explícitamente desde main.py