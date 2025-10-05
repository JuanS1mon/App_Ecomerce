#!/usr/bin/env python3
"""
Script para verificar y limpiar completamente el estado de alembic_version
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

def clean_alembic_version():
    """Limpiar completamente alembic_version"""
    try:
        with engine.connect() as connection:
            # Verificar contenido actual
            result = connection.execute(text("SELECT version_num FROM alembic_version"))
            versions = [row[0] for row in result.fetchall()]
            print(f"Versiones actuales en alembic_version: {versions}")
            
            # Eliminar todas las versiones
            connection.execute(text("DELETE FROM alembic_version"))
            connection.commit()
            print("✅ Tabla alembic_version limpiada")
            
            # Insertar solo la versión correcta
            connection.execute(text("INSERT INTO alembic_version (version_num) VALUES ('163506fcdd36')"))
            connection.commit()
            print("✅ Versión correcta insertada: 163506fcdd36")
            
            return True
            
    except Exception as e:
        print(f"❌ Error al limpiar alembic_version: {e}")
        return False

if __name__ == "__main__":
    print("🧹 Limpiando completamente alembic_version...")
    print(f"🔗 Conectando a: {SQLALCHEMY_DATABASE_URL}")
    
    success = clean_alembic_version()
    
    if success:
        print("\n✅ alembic_version limpiado e inicializado correctamente")
    else:
        print("\n❌ No se pudo limpiar alembic_version")