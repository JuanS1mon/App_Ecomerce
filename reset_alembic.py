#!/usr/bin/env python3
"""
Script para crear un Alembic completamente nuevo desde cero
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

def reset_alembic_completely():
    """Resetear Alembic completamente"""
    try:
        with engine.connect() as connection:
            # Eliminar la tabla alembic_version completamente
            try:
                connection.execute(text("DROP TABLE alembic_version"))
                connection.commit()
                print("✅ Tabla alembic_version eliminada")
            except Exception as e:
                print(f"ℹ️  No se pudo eliminar alembic_version (probablemente no existe): {e}")
            
            # Recrear la tabla alembic_version
            connection.execute(text("""
                CREATE TABLE alembic_version (
                    version_num VARCHAR(32) NOT NULL, 
                    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
                )
            """))
            connection.commit()
            print("✅ Tabla alembic_version recreada")
            
            # No insertar ninguna versión inicial - dejar que Alembic lo maneje
            print("ℹ️  Tabla alembic_version vacía, lista para inicialización")
            
            return True
            
    except Exception as e:
        print(f"❌ Error al resetear alembic_version: {e}")
        return False

if __name__ == "__main__":
    print("🔄 Reseteando Alembic completamente...")
    print(f"🔗 Conectando a: {SQLALCHEMY_DATABASE_URL}")
    
    success = reset_alembic_completely()
    
    if success:
        print("\n✅ Alembic reseteado completamente")
        print("Ahora ejecuta: alembic stamp head")
    else:
        print("\n❌ No se pudo resetear Alembic")