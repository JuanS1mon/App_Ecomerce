from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
from sqlalchemy.exc import OperationalError, InterfaceError
from fastapi import HTTPException

load_dotenv()  # carga las variables de entorno del archivo .env

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

SQLALCHEMY_DATABASE_URL = f"mssql+pyodbc://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}?driver={DB_DRIVER}"
SQLALCHEMY_MASTER_URL = f"mssql+pyodbc://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/master?driver={DB_DRIVER}"

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
        # Conectar a la base de datos master
        master_engine = create_engine(SQLALCHEMY_MASTER_URL, isolation_level="AUTOCOMMIT")
        with master_engine.connect() as connection:
            # Crear la base de datos si no existe
            connection.execute(text(f"IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = '{DB_NAME}') CREATE DATABASE {DB_NAME}"))
            # Configurar la base de datos para recuperación simple y auto-reducción
            connection.execute(text(f"ALTER DATABASE {DB_NAME} SET RECOVERY SIMPLE"))
            connection.execute(text(f"ALTER DATABASE {DB_NAME} SET AUTO_SHRINK ON"))
        # Crear las tablas en la base de datos
        Base.metadata.create_all(bind=engine)
        print("Base de datos creada exitosamente.")
    except (OperationalError, InterfaceError) as e:
        print(f"Error al crear la base de datos: {e}")

# Llamar a la función para crear la base de datos
create_database()