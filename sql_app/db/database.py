from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv
import os
from sqlalchemy.exc import OperationalError, InterfaceError, ProgrammingError
from fastapi import HTTPException

load_dotenv()  # carga las variables de entorno del archivo .env

DB_TYPE = os.getenv("DB_TYPE")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_DRIVER = os.getenv("DB_DRIVER")
POOL_SIZE = int(os.getenv("POOL_SIZE"))
MAX_OVERFLOW = int(os.getenv("MAX_OVERFLOW"))
POOL_TIMEOUT = int(os.getenv("POOL_TIMEOUT"))
POOL_PRE_PING = bool(os.getenv("POOL_PRE_PING"))
POOL_RECYCLE = int(os.getenv("POOL_RECYCLE"))

if DB_TYPE == "sqlserver":
    SQLALCHEMY_DATABASE_URL = f"mssql+pyodbc://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}?driver={DB_DRIVER}"
    SQLALCHEMY_MASTER_URL = f"mssql+pyodbc://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/master?driver={DB_DRIVER}"
elif DB_TYPE == "postgresql":
    SQLALCHEMY_DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
    SQLALCHEMY_MASTER_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/postgres"
else:
    raise ValueError("DB_TYPE debe ser 'sqlserver' o 'postgresql'")

# Crear el motor de conexión a la base de datos master
master_engine = create_engine(SQLALCHEMY_MASTER_URL, isolation_level="AUTOCOMMIT")

# Crear el motor de conexión a la base de datos específica
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=POOL_SIZE,  # Número de conexiones a mantener en el grupo
    max_overflow=MAX_OVERFLOW,  # Número de conexiones adicionales que se pueden crear más allá de pool_size
    pool_timeout=POOL_TIMEOUT,  # Tiempo de espera para obtener una conexión, en segundos
    pool_pre_ping=POOL_PRE_PING,  # Prueba la viabilidad de una conexión antes de usarla
    pool_recycle=POOL_RECYCLE  # Recicla las conexiones después de 1 hora
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
        # Lanzar una excepción HTTP con un mensaje de error en formato JSON
        yield None
    finally:
        if db is not None:
            db.close()

# Crear la base de datos si no existe
def create_database():
    try:
        with master_engine.connect() as connection:
            if DB_TYPE == "sqlserver":
                # Crear la base de datos si no existe (SQL Server)
                connection.execute(text(f"IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = '{DB_NAME}') CREATE DATABASE {DB_NAME}"))
                # Configurar la base de datos para recuperación simple y auto-reducción
                connection.execute(text(f"ALTER DATABASE {DB_NAME} SET RECOVERY SIMPLE"))
                connection.execute(text(f"ALTER DATABASE {DB_NAME} SET AUTO_SHRINK ON"))
            elif DB_TYPE == "postgresql":
                # Verificar si la base de datos ya existe (PostgreSQL)
                result = connection.execute(text(f"SELECT 1 FROM pg_database WHERE datname = '{DB_NAME}'"))
                if not result.scalar():
                    # Crear la base de datos si no existe (PostgreSQL)
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

# Llamar a la función para crear la base de datos y las tablas
create_database()
create_tables()