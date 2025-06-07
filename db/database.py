from sqlalchemy import create_engine, text, MetaData, Table, inspect
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.ext.declarative import DeferredReflection
from dotenv import load_dotenv
import os
import importlib
import sys
from sqlalchemy.exc import OperationalError, InterfaceError, ProgrammingError, NoReferencedTableError
from fastapi import HTTPException

# Cargar variables de entorno
load_dotenv()

# Detectar si estamos en Heroku
DATABASE_URL = os.getenv("DATABASE_URL")
is_heroku = DATABASE_URL is not None

if is_heroku:
    # Si estamos en Heroku, usar DATABASE_URL proporcionado
    if DATABASE_URL.startswith("postgres://"):
        # Convertir postgres:// a postgresql:// para SQLAlchemy
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    
    SQLALCHEMY_DATABASE_URL = DATABASE_URL
    # No necesitamos una conexión master en Heroku
    master_engine = None
else:
    # Configuración local usando variables de entorno
    DB_TYPE = os.getenv("DB_TYPE", "postgresql").split('#')[0].strip()  # Limpiar comentarios
    
    if DB_TYPE == "sqlite":
        # Configuración para SQLite
        SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")
        master_engine = None
    else:
        # Configuración para PostgreSQL/SQL Server
        DB_USER = os.getenv("DB_USER", "postgres")
        DB_PASSWORD = os.getenv("DB_PASSWORD", "")
        DB_HOST = os.getenv("DB_HOST", "localhost")
        DB_NAME = os.getenv("DB_NAME", "sqlapp")
        DB_DRIVER = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")

        # Valores seguros para el pool con predeterminados
        POOL_SIZE = int(os.getenv("POOL_SIZE", "5"))
        MAX_OVERFLOW = int(os.getenv("MAX_OVERFLOW", "10"))
        POOL_TIMEOUT = int(os.getenv("POOL_TIMEOUT", "30"))
        POOL_PRE_PING = os.getenv("POOL_PRE_PING", "True").lower() in ('true', '1', 't')
        POOL_RECYCLE = int(os.getenv("POOL_RECYCLE", "3600"))
        
        # Construir URLs según el tipo de base de datos
        if DB_TYPE == "sqlserver":
            SQLALCHEMY_DATABASE_URL = f"mssql+pyodbc://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}?driver={DB_DRIVER}"
            SQLALCHEMY_MASTER_URL = f"mssql+pyodbc://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/master?driver={DB_DRIVER}"
        elif DB_TYPE == "postgresql":
            SQLALCHEMY_DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
            SQLALCHEMY_MASTER_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/postgres"
        else:
            raise ValueError("DB_TYPE debe ser 'sqlserver', 'postgresql' o 'sqlite'")
        
        # Crear el motor de conexión a la base de datos master (solo en desarrollo)
        if DB_TYPE != "sqlite":
            master_engine = create_engine(SQLALCHEMY_MASTER_URL, isolation_level="AUTOCOMMIT")

# Configuración de pool para Heroku
if is_heroku:
    # Configuración recomendada para Heroku PostgreSQL
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        pool_size=5,
        max_overflow=10,
        pool_timeout=30,
        pool_pre_ping=True,
        pool_recycle=1800  # 30 minutos, recomendado para Heroku
    )
else:
    # Usar configuración local
    if os.getenv("DB_TYPE", "postgresql") == "sqlite":
        # Configuración específica para SQLite
        engine = create_engine(
            SQLALCHEMY_DATABASE_URL,
            connect_args={"check_same_thread": False}
        )
    else:
        # Configuración para PostgreSQL/SQL Server
        POOL_SIZE = int(os.getenv("POOL_SIZE", "5"))
        MAX_OVERFLOW = int(os.getenv("MAX_OVERFLOW", "10"))
        POOL_TIMEOUT = int(os.getenv("POOL_TIMEOUT", "30"))
        POOL_PRE_PING = os.getenv("POOL_PRE_PING", "True").lower() in ('true', '1', 't')
        POOL_RECYCLE = int(os.getenv("POOL_RECYCLE", "3600"))
        
        engine = create_engine(
            SQLALCHEMY_DATABASE_URL,
            pool_size=POOL_SIZE,
            max_overflow=MAX_OVERFLOW,
            pool_timeout=POOL_TIMEOUT,
            pool_pre_ping=POOL_PRE_PING,
            pool_recycle=POOL_RECYCLE
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
    # Omitir en Heroku
    if is_heroku:
        print("Ejecutando en Heroku - omitiendo creación de base de datos")
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
                else:
                    print(f"La base de datos '{DB_NAME}' ya existe.")
        print("Base de datos verificada o creada exitosamente.")
    except (OperationalError, InterfaceError, ProgrammingError) as e:
        print(f"Error al crear la base de datos: {e}")

# Función para cargar el modelo Roles primero
def ensure_roles_model():
    try:
        # Intentar importar el modelo Roles existente
        try:
            importlib.import_module("db.models.roles")
            print("Modelo Roles importado correctamente.")
        except ImportError:
            # Si no existe, crearlo
            import os
            models_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'db', 'models')
            os.makedirs(models_dir, exist_ok=True)
            
            roles_file_path = os.path.join(models_dir, 'roles.py')
            
            if not os.path.exists(roles_file_path):
                with open(roles_file_path, 'w') as f:
                    f.write("""from sqlalchemy import Column, Integer, String
try:
    from ...db.database import Base
except ImportError:
    from sql_app.db.database import Base
class Roles(Base):
    __tablename__ = "Roles"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), unique=True)
    descripcion = Column(String(255), nullable=True)
""")
                print(f"Modelo Roles creado en: {roles_file_path}")
                # Recargar el módulo después de crearlo
                importlib.import_module("db.models.roles")
        
        # Crear solo la tabla Roles primero
        from sqlalchemy import MetaData
        temp_metadata = MetaData()
        for table_name, table in Base.metadata.tables.items():
            if table_name == "Roles":
                table.tometadata(temp_metadata)
                temp_metadata.create_all(bind=engine)
                print("Tabla Roles creada exitosamente.")
                break
                
    except Exception as e:
        print(f"Error al asegurar el modelo Roles: {e}")
        import traceback
        traceback.print_exc()

# Función para crear específicamente las tablas relacionadas con OT
def create_ot_tables():
    try:        # Importar los modelos OT
        from ..Services.app_stock.ot.model_ot import OT, Operacion, ReporteTiempo
        
        # Crear una conexión directa para ejecutar SQL puro
        connection = engine.connect()
        
        # Eliminar las tablas existentes si existen para forzar su recreación
        print("Eliminando tablas de OT existentes para recrearlas...")
        try:
            connection.execute(text("DROP TABLE IF EXISTS reportes_tiempo"))
            print("Tabla reportes_tiempo eliminada")
        except Exception as e:
            print(f"Error al eliminar tabla reportes_tiempo: {e}")
        
        try:
            connection.execute(text("DROP TABLE IF EXISTS operaciones"))
            print("Tabla operaciones eliminada")
        except Exception as e:
            print(f"Error al eliminar tabla operaciones: {e}")
        
        try:
            connection.execute(text("DROP TABLE IF EXISTS ot"))
            print("Tabla ot eliminada")
        except Exception as e:
            print(f"Error al eliminar tabla ot: {e}")
            
        connection.commit()
        
        # Crear metadatos específicos para las tablas de OT
        metadata = MetaData()
        
        # Obtener las definiciones de tablas y transferirlas a los metadatos
        ot_table = Base.metadata.tables["ot"]
        ot_table.tometadata(metadata)
        
        operaciones_table = Base.metadata.tables["operaciones"]
        operaciones_table.tometadata(metadata)
        
        reportes_tiempo_table = Base.metadata.tables["reportes_tiempo"]
        reportes_tiempo_table.tometadata(metadata)
        
        # Crear las tablas en el orden correcto
        metadata.create_all(bind=engine)
        print("Tablas de OT creadas exitosamente")
        
        # Verificar que las columnas se hayan creado correctamente
        inspector = inspect(engine)
        columns = inspector.get_columns("ot")
        column_names = [col['name'] for col in columns]
        print(f"Columnas creadas en tabla OT: {column_names}")
        
    except Exception as e:
        print(f"Error al crear tablas de OT: {e}")
        import traceback
        traceback.print_exc()

# Crear las tablas en la base de datos
def create_tables():
    try:
        # Primero asegurar que exista la tabla Roles
        ensure_roles_model()
        
        # Asegurar que existan las tablas de OT
        create_ot_tables()
        
        # Ahora crear el resto de las tablas
        tables_to_create = []
        for table_name, table in Base.metadata.tables.items():
            if table_name != "Roles" and table_name not in ["ot", "operaciones", "reportes_tiempo"]:
                tables_to_create.append(table)
        
        if tables_to_create:
            # Crear todas las demás tablas
            metadata = MetaData()
            for table in tables_to_create:
                table.tometadata(metadata)
            metadata.create_all(bind=engine)
            
        print("Tablas creadas exitosamente.")
    except NoReferencedTableError as e:
        print(f"Error de tabla referenciada: {e}")
        # Si falla porque falta una tabla referenciada, intenta manejar caso por caso
        if "Roles" in str(e):
            ensure_roles_model()
            # Intentar crear tablas nuevamente
            Base.metadata.create_all(bind=engine)
    except (OperationalError, InterfaceError, ProgrammingError) as e:
        print(f"Error al crear tablas: {e}")
        import traceback
        traceback.print_exc()

# La base de datos se crea pero las tablas no se crean automáticamente
# para evitar problemas de orden de creación
create_database()  # Se omitirá en Heroku
# Las tablas se crearán explícitamente desde main.py