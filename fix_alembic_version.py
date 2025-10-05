#!/usr/bin/env python3
"""
Script para revisar y corregir el estado de alembic_version en la base de datos
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

def check_alembic_version():
    """Verificar el estado actual de alembic_version"""
    try:
        with engine.connect() as connection:
            # Verificar si la tabla alembic_version existe
            result = connection.execute(text("""
                SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_NAME = 'alembic_version'
            """))
            
            if not result.fetchone():
                print("❌ La tabla alembic_version no existe")
                return None
            
            # Obtener la versión actual
            result = connection.execute(text("SELECT version_num FROM alembic_version"))
            version = result.scalar()
            
            if version:
                print(f"✅ Versión actual en alembic_version: {version}")
                return version
            else:
                print("❌ No hay versión registrada en alembic_version")
                return None
                
    except Exception as e:
        print(f"❌ Error al verificar alembic_version: {e}")
        return None

def fix_alembic_version():
    """Corregir la versión de alembic_version"""
    current_version = check_alembic_version()
    
    if current_version == "a9be0c37e699":
        print("🔧 Corrigiendo versión incorrecta a9be0c37e699...")
        try:
            with engine.connect() as connection:
                # Actualizar a la versión correcta (163506fcdd36 es la última válida)
                connection.execute(text("UPDATE alembic_version SET version_num = '163506fcdd36'"))
                connection.commit()
                print("✅ Versión corregida a 163506fcdd36")
                return True
        except Exception as e:
            print(f"❌ Error al corregir versión: {e}")
            return False
    elif current_version == "163506fcdd36":
        print("✅ La versión ya está correcta")
        return True
    elif current_version is None:
        print("🔧 Insertando versión inicial...")
        try:
            with engine.connect() as connection:
                connection.execute(text("INSERT INTO alembic_version (version_num) VALUES ('163506fcdd36')"))
                connection.commit()
                print("✅ Versión inicial insertada: 163506fcdd36")
                return True
        except Exception as e:
            print(f"❌ Error al insertar versión: {e}")
            return False
    else:
        print(f"⚠️  Versión desconocida: {current_version}")
        return False

if __name__ == "__main__":
    print("🔍 Verificando estado de alembic_version...")
    print(f"🔗 Conectando a: {SQLALCHEMY_DATABASE_URL}")
    
    success = fix_alembic_version()
    
    if success:
        print("\n✅ Estado de alembic_version corregido exitosamente")
        print("Ahora puedes ejecutar: alembic upgrade head")
    else:
        print("\n❌ No se pudo corregir el estado de alembic_version")
        print("Verifica la conexión a la base de datos y los permisos")