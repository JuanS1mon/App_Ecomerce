from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv
import os
from sqlalchemy.exc import OperationalError, InterfaceError, ProgrammingError
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
    DB_TYPE = os.getenv("DB_TYPE", "postgresql")
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
        raise ValueError("DB_TYPE debe ser 'sqlserver' o 'postgresql'")
    
    # Crear el motor de conexión a la base de datos master (solo en desarrollo)
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

# Crear las tablas en la base de datos
def create_tables():
    try:
        Base.metadata.create_all(bind=engine)
        print("Tablas creadas exitosamente.")
    except (OperationalError, InterfaceError, ProgrammingError) as e:
        print(f"Error al crear tablas: {e}")

# Inicialización condicional
create_database()  # Se omitirá en Heroku
create_tables()    # Siempre se ejecuta