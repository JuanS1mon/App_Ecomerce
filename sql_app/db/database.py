from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

#SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db" 
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"
DB_USER = "SA"
DB_PASSWORD = "LaCrujia_3261"
DB_HOST = "LocalHost"
DB_NAME = "pruebas"
DB_DRIVER = "ODBC Driver 17 for SQL Server"

SQLALCHEMY_DATABASE_URL = f"mssql+pyodbc://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}?driver={DB_DRIVER}"


engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=10,  # Número de conexiones a mantener en el grupo
    max_overflow=20,  # Número de conexiones adicionales que se pueden crear más allá de pool_size
    pool_timeout=10,  # Tiempo de espera para obtener una conexión, en segundos
    pool_pre_ping=True,  # Prueba la viabilidad de una conexión antes de usarla
    pool_recycle=3600  # Recicla las conexiones después de 1 hora
)
SessionLocal = sessionmaker(autocommit=False, autoflush=True, bind=engine)

Base = declarative_base()

Base.metadata.create_all(bind=engine) # que es metadata ?? https://docs.sqlalchemy.org/en/14/core/metadata.html

# Dependencia de base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()