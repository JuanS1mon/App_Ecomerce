#!/usr/bin/env python3
"""
Script para crear manualmente la tabla alembic_version e inicializar con la versión correcta
"""

import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Cargar variables de entorno
load_dotenv()

# Configuración de base de datos
DB_TYPE = os.getenv("DB_TYPE", "sqlserver").split('#')[0].strip()
DB_USER = os.getenv("DB_USER", "sa")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "sqlapp")
DB_DRIVER = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")

if DB_TYPE == "sqlserver":
    SQLALCHEMY_DATABASE_URL = f"mssql+pyodbc://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}?driver={DB_DRIVER}"
else:
    SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./sql_app.db")

engine = create_engine(SQLALCHEMY_DATABASE_URL)

def create_alembic_version_table():
    """Crear la tabla alembic_version manualmente"""
    try:
        with engine.connect() as connection:
            # Crear la tabla alembic_version
            connection.execute(text("""
                CREATE TABLE alembic_version (
                    version_num VARCHAR(32) NOT NULL, 
                    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
                )
            """))
            connection.commit()
            print("✅ Tabla alembic_version creada exitosamente")
            
            # Insertar la versión actual (163506fcdd36 es la última migración válida)
            connection.execute(text("INSERT INTO alembic_version (version_num) VALUES ('163506fcdd36')"))
            connection.commit()
            print("✅ Versión inicial insertada: 163506fcdd36")
            
            return True
            
    except Exception as e:
        print(f"❌ Error al crear tabla alembic_version: {e}")
        if "already exists" in str(e).lower() or "ya existe" in str(e).lower():
            print("ℹ️  La tabla alembic_version ya existe")
            try:
                with engine.connect() as connection:
                    # Solo insertar la versión si la tabla está vacía
                    result = connection.execute(text("SELECT COUNT(*) FROM alembic_version"))
                    count = result.scalar()
                    
                    if count == 0:
                        connection.execute(text("INSERT INTO alembic_version (version_num) VALUES ('163506fcdd36')"))
                        connection.commit()
                        print("✅ Versión inicial insertada: 163506fcdd36")
                    else:
                        # Actualizar la versión si ya existe pero es incorrecta
                        connection.execute(text("UPDATE alembic_version SET version_num = '163506fcdd36'"))
                        connection.commit()
                        print("✅ Versión actualizada a: 163506fcdd36")
                    
                    return True
            except Exception as e2:
                print(f"❌ Error al manejar tabla existente: {e2}")
                return False
        return False

if __name__ == "__main__":
    print("🔧 Creando tabla alembic_version manualmente...")
    print(f"🔗 Conectando a: {SQLALCHEMY_DATABASE_URL}")
    
    success = create_alembic_version_table()
    
    if success:
        print("\n✅ Tabla alembic_version creada e inicializada exitosamente")
        print("Ahora puedes ejecutar: alembic upgrade head")
    else:
        print("\n❌ No se pudo crear la tabla alembic_version")
        print("Verifica la conexión a la base de datos y los permisos")